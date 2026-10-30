from django.test import TestCase
from unittest.mock import patch

from accounts.factories import make_job, make_user
from jobs.models import Job
from payments.models import Transaction, Wallet
from payments.services import (
    PaymentError,
    confirm_and_release,
    confirm_escrow_payment,
    fail_escrow_payment,
    mark_work_done,
    start_escrow_payment,
)

# Create your tests here.

class EscrowFundingTests(TestCase):
    def setUp(self):
        self.employer = make_user("emp", "employer")
        self.worker = make_user("wrk", "worker")
        self.job = make_job(self.employer, self.worker, status=Job.Status.ACCEPTED)

    def test_cannot_start_payment_before_worker_accepts(self):
        self.job.status = Job.Status.REQUESTED
        self.job.save()
        with self.assertRaises(PaymentError):
            start_escrow_payment(self.job)

    def test_start_payment_reuses_pending_deposit(self):
        first = start_escrow_payment(self.job)
        second = start_escrow_payment(self.job)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(first.amount, 3000)
        self.assertEqual(first.status, Transaction.Status.PENDING)

    def test_successful_payment_funds_the_job(self):
        txn = start_escrow_payment(self.job)
        confirm_escrow_payment(txn.pk, self.employer, "REF-1")
        txn.refresh_from_db()
        self.job.refresh_from_db()
        self.assertEqual(txn.status, Transaction.Status.COMPLETED)
        self.assertEqual(txn.gateway_reference, "REF-1")
        self.assertEqual(self.job.status, Job.Status.FUNDED)

    def test_other_employer_cannot_confirm_payment(self):
        stranger = make_user("stranger", "employer")
        txn = start_escrow_payment(self.job)
        with self.assertRaises(PaymentError):
            confirm_escrow_payment(txn.pk, stranger, "REF-X")
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, Job.Status.ACCEPTED)

    def test_payment_cannot_be_confirmed_twice(self):
        txn = start_escrow_payment(self.job)
        confirm_escrow_payment(txn.pk, self.employer, "REF-1")
        with self.assertRaises(PaymentError):
            confirm_escrow_payment(txn.pk, self.employer, "REF-2")

    def test_failed_payment_leaves_job_accepted(self):
        txn = start_escrow_payment(self.job)
        fail_escrow_payment(txn.pk, self.employer)
        txn.refresh_from_db()
        self.job.refresh_from_db()
        self.assertEqual(txn.status, Transaction.Status.FAILED)
        self.assertEqual(self.job.status, Job.Status.ACCEPTED)


class ReleaseTests(TestCase):
    def setUp(self):
        self.employer = make_user("emp", "employer")
        self.worker = make_user("wrk", "worker")
        self.job = make_job(
            self.employer, self.worker, status=Job.Status.FUNDED, wage=4000
        )
        Transaction.objects.create(
            job=self.job,
            amount=4000,
            transaction_type=Transaction.TransactionType.DEPOSIT,
            status=Transaction.Status.COMPLETED,
            gateway_reference="REF-1",
        )

    def test_only_the_hired_worker_can_mark_work_done(self):
        other_worker = make_user("other", "worker")
        with self.assertRaises(PaymentError):
            mark_work_done(self.job.pk, other_worker)
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, Job.Status.FUNDED)

    def test_release_pays_the_worker_wallet(self):
        mark_work_done(self.job.pk, self.worker)
        amount = confirm_and_release(self.job.pk, self.employer)

        self.job.refresh_from_db()
        wallet = Wallet.objects.get(user=self.worker)
        releases = Transaction.objects.filter(
            job=self.job, transaction_type=Transaction.TransactionType.RELEASE
        )
        self.assertEqual(amount, 4000)
        self.assertEqual(wallet.balance, 4000)
        self.assertEqual(self.job.status, Job.Status.COMPLETED)
        self.assertEqual(releases.count(), 1)

    def test_cannot_release_before_work_is_done(self):
        with self.assertRaises(PaymentError):
            confirm_and_release(self.job.pk, self.employer)
        self.assertFalse(Wallet.objects.filter(user=self.worker).exists())

    def test_only_the_employer_can_release(self):
        mark_work_done(self.job.pk, self.worker)
        with self.assertRaises(PaymentError):
            confirm_and_release(self.job.pk, self.worker)
        self.assertFalse(Wallet.objects.filter(user=self.worker).exists())

    def test_worker_cannot_be_paid_twice(self):
        mark_work_done(self.job.pk, self.worker)
        confirm_and_release(self.job.pk, self.employer)
        with self.assertRaises(PaymentError):
            confirm_and_release(self.job.pk, self.employer)

        wallet = Wallet.objects.get(user=self.worker)
        releases = Transaction.objects.filter(
            job=self.job, transaction_type=Transaction.TransactionType.RELEASE
        )
        self.assertEqual(wallet.balance, 4000)
        self.assertEqual(releases.count(), 1)

    def test_failure_midway_rolls_everything_back(self):
        mark_work_done(self.job.pk, self.worker)
        with patch.object(Transaction.objects, "create", side_effect=RuntimeError("boom")):
            with self.assertRaises(RuntimeError):
                confirm_and_release(self.job.pk, self.employer)

        self.job.refresh_from_db()
        self.assertEqual(self.job.status, Job.Status.WORK_DONE)
        self.assertFalse(Wallet.objects.filter(user=self.worker).exists())
