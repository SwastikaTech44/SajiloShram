from django.shortcuts import render

from accounts.views import dashboard
from jobs.models import Review
from workers.models import District, Skill, WorkerProfile


def home(request):
    if request.user.is_authenticated:
        return dashboard(request)

    verified = WorkerProfile.objects.filter(nid_status=WorkerProfile.NIDStatus.VERIFIED)
    featured = (
        verified.filter(is_available=True)
        .select_related('user', 'municipality__district')
        .prefetch_related('skills')
        .order_by('-created_at')[:4]
    )
    reviews = (
        Review.objects.exclude(comment='')
        .select_related('reviewer', 'job__worker')
        .order_by('-created_at')[:3]
    )
    context = {
        'districts': District.objects.order_by('name'),
        'skills': Skill.objects.order_by('name'),
        'featured': featured,
        'reviews': reviews,
        'stats': {
            'districts': District.objects.count(),
            'skills': Skill.objects.count(),
            'verified_workers': verified.count(),
        },
    }
    return render(request, 'landing.html', context)