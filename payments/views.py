from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from jobs.models import Job

from .models import Transaction
from .services import (
    PaymentError,
    confirm_escrow_payment,
    fail_escrow_payment,
    make_mock_reference,
    start_escrow_payment,
)


@login_required
def checkout(request, job_id):
    job = get_object_or_404(Job, pk=job_id, employer=request.user)

    if job.status != Job.Status.ACCEPTED:
        messages.error(request, "This job is not waiting for payment.")
        return redirect("job_detail", job_id=job.pk)

    if request.method == "POST":
        try:
            txn = start_escrow_payment(job)
        except PaymentError as exc:
            messages.error(request, str(exc))
            return redirect("job_detail", job_id=job.pk)
        return redirect("mock_gateway", txn_id=txn.pk)

    return render(request, "payments/checkout.html", {"job": job})


@login_required
def mock_gateway(request, txn_id):
    txn = get_object_or_404(
        Transaction,
        pk=txn_id,
        job__employer=request.user,
        status=Transaction.Status.PENDING,
    )

    if request.method == "POST":
        outcome = request.POST.get("outcome")
        try:
            if outcome == "success":
                confirm_escrow_payment(txn.pk, request.user, make_mock_reference())
                messages.success(request, "Payment received. The money is held in escrow.")
            else:
                fail_escrow_payment(txn.pk, request.user)
                messages.error(request, "Payment cancelled. You can try again.")
        except PaymentError as exc:
            messages.error(request, str(exc))
        return redirect("job_detail", job_id=txn.job_id)

    return render(request, "payments/mock_gateway.html", {"txn": txn})