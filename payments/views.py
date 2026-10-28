from django.views.decorators.http import require_POST
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from jobs.models import Job

from . import esewa
from .models import Transaction
from .services import (
    PaymentError,
    confirm_escrow_payment,
    fail_escrow_payment,
    make_mock_reference,
    start_escrow_payment,
    confirm_and_release,
    mark_work_done,
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
        
        if settings.PAYMENT_GATEWAY == "esewa":
            return redirect("esewa_pay", txn_id=txn.pk)
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

@login_required
def esewa_pay(request, txn_id):
    txn = get_object_or_404(
        Transaction,
        pk=txn_id,
        job__employer=request.user,
        status=Transaction.Status.PENDING,
    )
    form = esewa.build_payment_form(
        txn,
        success_url=request.build_absolute_uri(reverse("esewa_success")),
        failure_url=request.build_absolute_uri(reverse("esewa_failure")),
    )
    return render(request, "payments/esewa_redirect.html", form)


@login_required
def esewa_success(request):
    try:
        data = esewa.decode_and_verify(request.GET.get("data", ""))

        if data["status"] != "COMPLETE":
            raise esewa.EsewaError("eSewa did not mark this payment as complete.")
        if data["product_code"] != settings.ESEWA_PRODUCT_CODE:
            raise esewa.EsewaError("This payment was made to a different merchant.")

        txn = Transaction.objects.get(pk=esewa.txn_id_from_uuid(data["transaction_uuid"]))

        if esewa.to_decimal(data["total_amount"]) != Decimal(txn.amount):
            raise esewa.EsewaError("The paid amount does not match the job wage.")

        confirm_escrow_payment(txn.pk, request.user, data.get("transaction_code", ""))
    except (esewa.EsewaError, PaymentError) as exc:
        messages.error(request, str(exc))
        return redirect("job_list")
    except Transaction.DoesNotExist:
        messages.error(request, "We could not find that payment.")
        return redirect("job_list")

    messages.success(request, "Payment received. The money is held in escrow.")
    return redirect("job_detail", job_id=txn.job_id)


@login_required
def esewa_failure(request):
    messages.error(request, "The eSewa payment was cancelled or failed. You can try again.")
    return redirect("job_list")

@login_required
@require_POST
def work_done(request, job_id):
    job = get_object_or_404(Job, pk=job_id, worker=request.user)
    try:
        mark_work_done(job.pk, request.user)
        messages.success(request, "Marked as done. Waiting for the employer to confirm.")
    except PaymentError as exc:
        messages.error(request, str(exc))
    return redirect("job_detail", job_id=job.pk)


@login_required
@require_POST
def confirm_release(request, job_id):
    job = get_object_or_404(Job, pk=job_id, employer=request.user)
    try:
        amount = confirm_and_release(job.pk, request.user)
        messages.success(
            request,
            f"Work confirmed. Rs. {amount} was released to {job.worker.username}'s wallet.",
        )
    except PaymentError as exc:
        messages.error(request, str(exc))
    return redirect("job_detail", job_id=job.pk)