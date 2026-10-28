import uuid

from django.db import transaction

from jobs.models import Job

from .models import Transaction, Wallet


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

def mark_work_done(job_id, worker):
    with transaction.atomic():
        job = Job.objects.select_for_update().get(pk=job_id)

        if job.worker_id != worker.id:
            raise PaymentError("Only the hired worker can do this.")
        if job.status != Job.Status.FUNDED:
            raise PaymentError("This job is not in progress.")

        job.move_to(Job.Status.WORK_DONE)


def confirm_and_release(job_id, employer):
    with transaction.atomic():
        job = Job.objects.select_for_update().get(pk=job_id)

        if job.employer_id != employer.id:
            raise PaymentError("Only the employer can confirm this job.")
        if job.status != Job.Status.WORK_DONE:
            raise PaymentError("The worker has not marked this job as done.")

        deposit = Transaction.objects.filter(
            job=job,
            transaction_type=Transaction.TransactionType.DEPOSIT,
            status=Transaction.Status.COMPLETED,
        ).first()
        if deposit is None:
            raise PaymentError("No escrow payment was found for this job.")

        already_released = Transaction.objects.filter(
            job=job,
            transaction_type=Transaction.TransactionType.RELEASE,
        ).exists()
        if already_released:
            raise PaymentError("This payment was already released.")

        wallet, created = Wallet.objects.select_for_update().get_or_create(
            user=job.worker
        )
        wallet.balance += deposit.amount
        wallet.save(update_fields=["balance", "updated_at"])

        Transaction.objects.create(
            job=job,
            amount=deposit.amount,
            transaction_type=Transaction.TransactionType.RELEASE,
            status=Transaction.Status.COMPLETED,
            gateway_reference=f"WALLET-{uuid.uuid4().hex[:12].upper()}",
        )

        job.move_to(Job.Status.COMPLETED)
        return deposit.amount