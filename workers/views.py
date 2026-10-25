from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import WorkerProfileForm
from .models import WorkerProfile


@login_required
def edit_profile(request):
    profile, created = WorkerProfile.objects.get_or_create(
        user=request.user,
        defaults={'daily_rate': 0, 'ward_no': 1}
    )
    if request.method == 'POST':
        form = WorkerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = WorkerProfileForm(instance=profile)
    return render(request, 'workers/edit_profile.html', {'form': form})


@login_required
def worker_list(request):
    workers = WorkerProfile.objects.select_related('user', 'municipality').all()
    return render(request, 'workers/worker_list.html', {'workers': workers})


def worker_detail(request, profile_id):
    worker = get_object_or_404(WorkerProfile, id=profile_id)
    return render(request, 'workers/worker_detail.html', {'worker': worker})