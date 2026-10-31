from django.db.models import Q
from rest_framework import viewsets

from .models import Job
from .serializers import JobSerializer


class JobViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = JobSerializer

    def get_queryset(self):
        user = self.request.user
        return (
            Job.objects
            .filter(Q(employer=user) | Q(worker=user))
            .select_related('employer', 'worker', 'review')
            .order_by('-created_at')
        )