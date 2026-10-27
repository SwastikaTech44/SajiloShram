import uuid

from django.db import transaction

from jobs.models import Job

from .models import Transaction


class PaymentError(Exception):
    """Raised when a payment step is not allowed."""


def start_escrow_payment(job):
    if job.status != Job.Status.ACCEPTED:
        raise PaymentError("This job is not waiting for payment.")

    txn = Transaction.objects.filter(
        job=job,
        transaction_type=Transaction.TransactionType.DEPOSIT,
        status=Transaction.Status.PENDING,
    ).first()

    if txn is None:
        txn = Transaction.objects.create(
            job=job,
            amount=job.agreed_wage,
            transaction_type=Transaction.TransactionType.DEPOSIT,
        )
    return txn


def confirm_escrow_payment(txn_id, employer, gateway_reference):
    with transaction.atomic():
        txn = Transaction.objects.select_for_update().get(pk=txn_id)
        job = Job.objects.select_for_update().get(pk=txn.job_id)

        if job.employer_id != employer.id:
            raise PaymentError("This payment does not belong to you.")
        if txn.status != Transaction.Status.PENDING:
            raise PaymentError("This payment was already processed.")
        if job.status != Job.Status.ACCEPTED:
            raise PaymentError("This job is not waiting for payment.")

        txn.status = Transaction.Status.COMPLETED
        txn.gateway_reference = gateway_reference
        txn.save(update_fields=["status", "gateway_reference"])

        job.move_to(Job.Status.FUNDED)


def fail_escrow_payment(txn_id, employer):
    with transaction.atomic():
        txn = Transaction.objects.select_for_update().select_related("job").get(pk=txn_id)

        if txn.job.employer_id != employer.id:
            raise PaymentError("This payment does not belong to you.")
        if txn.status != Transaction.Status.PENDING:
            raise PaymentError("This payment was already processed.")

        txn.status = Transaction.Status.FAILED
        txn.save(update_fields=["status"])


def make_mock_reference():
    return f"MOCK-{uuid.uuid4().hex[:12].upper()}"