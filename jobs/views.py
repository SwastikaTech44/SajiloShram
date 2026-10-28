from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from workers.models import WorkerProfile

from django.db import IntegrityError, transaction

from .forms import JobForm, HireRequestForm, ReviewForm
from .models import Job, Review


@login_required
def create_job(request):
    if request.user.role != 'employer':
        messages.error(request, 'Only employers can post jobs.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            job.save()
            return redirect('job_list')
    else:
        form = JobForm()
    return render(request, 'jobs/create_job.html', {'form': form})


@login_required
def job_list(request):
    if request.user.role == 'worker':
        jobs = Job.objects.filter(worker=request.user)
    else:
        jobs = Job.objects.filter(employer=request.user)
    jobs = jobs.select_related('employer', 'worker').order_by('-created_at')
    return render(request, 'jobs/job_list.html', {'jobs': jobs})


@login_required
def job_detail(request, job_id):
    job = get_object_or_404(
        Job,
        Q(employer=request.user) | Q(worker=request.user),
        id=job_id,
    )
    return render(request, 'jobs/job_detail.html', {'job': job})


@login_required
def request_hire(request, worker_pk):
    if request.user.role != 'employer':
        messages.error(request, 'Only employers can hire workers.')
        return redirect('dashboard')

    profile = get_object_or_404(WorkerProfile, pk=worker_pk)

    if request.method == 'POST':
        form = HireRequestForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            job.worker = profile.user
            job.save()
            messages.success(request, 'Hire request sent.')
            return redirect('job_list')
    else:
        form = HireRequestForm()

    return render(request, 'jobs/hire_request.html', {'form': form, 'profile': profile})


@login_required
@require_POST
def respond_job(request, pk):
    job = get_object_or_404(Job, pk=pk, worker=request.user)
    action = request.POST.get('action')

    if action == 'accept':
        new_status = Job.Status.ACCEPTED
    elif action == 'decline':
        new_status = Job.Status.DECLINED
    else:
        messages.error(request, 'Unknown action.')
        return redirect('job_list')

    try:
        job.move_to(new_status)
        messages.success(request, f'Request {job.get_status_display().lower()}.')
    except ValueError:
        messages.error(request, 'This request can no longer be changed.')
    return redirect('job_list')


@login_required
def review_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id, employer=request.user)

    if job.status != Job.Status.COMPLETED:
        messages.error(request, "You can review a worker only after the job is completed.")
        return redirect("job_detail", job_id=job.pk)

    if Review.objects.filter(job=job).exists():
        messages.error(request, "You have already reviewed this job.")
        return redirect("job_detail", job_id=job.pk)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.job = job
            review.reviewer = request.user
            try:
                with transaction.atomic():
                    review.save()
            except IntegrityError:
                messages.error(request, "You have already reviewed this job.")
                return redirect("job_detail", job_id=job.pk)
            messages.success(request, "Thank you! Your review was saved.")
            return redirect("job_detail", job_id=job.pk)
    else:
        form = ReviewForm()

    return render(request, "jobs/review_form.html", {"form": form, "job": job})