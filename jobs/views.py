from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import JobForm
from .models import Job


@login_required
def create_job(request):
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
    jobs = Job.objects.filter(employer=request.user).order_by('-created_at')
    return render(request, 'jobs/job_list.html', {'jobs': jobs})


@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user)
    return render(request, 'jobs/job_detail.html', {'job': job})