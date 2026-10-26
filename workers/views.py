from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .filters import WorkerFilter
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
    base = (
        WorkerProfile.objects
        .select_related('user', 'municipality__district')
        .prefetch_related('skills')
        .order_by('daily_rate')
    )
    worker_filter = WorkerFilter(request.GET, queryset=base)
    return render(request, 'workers/worker_list.html', {
        'filter': worker_filter,
        'workers': worker_filter.qs,
    })


def worker_detail(request, profile_id):
    worker = get_object_or_404(WorkerProfile, id=profile_id)
    return render(request, 'workers/worker_detail.html', {'worker': worker})


@login_required
@require_POST
def upload_audio(request):
    if request.user.role != 'worker':
        return JsonResponse({'error': 'Only workers can upload an intro.'}, status=403)

    audio = request.FILES.get('audio')
    if not audio:
        return JsonResponse({'error': 'No audio received.'}, status=400)
    if audio.size > 2 * 1024 * 1024:
        return JsonResponse({'error': 'Recording too large (max 2 MB).'}, status=400)

    content_type = audio.content_type or ''
    if 'mp4' in content_type:
        ext = 'mp4'
    elif 'ogg' in content_type:
        ext = 'ogg'
    else:
        ext = 'webm'

    profile, _ = WorkerProfile.objects.get_or_create(
        user=request.user,
        defaults={'daily_rate': 0, 'ward_no': 1}
    )
    profile.audio_intro.save(f'intro_{request.user.id}.{ext}', audio)
    return JsonResponse({'ok': True, 'url': profile.audio_intro.url})


@login_required
def record_intro(request):
    return render(request, 'workers/record_intro.html')