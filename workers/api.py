from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from .filters import WorkerFilter
from .models import WorkerProfile
from .serializers import WorkerSerializer


class WorkerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WorkerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = WorkerFilter
    queryset = (
        WorkerProfile.objects
        .select_related('user', 'municipality__district')
        .prefetch_related('skills')
        .order_by('daily_rate', 'id')
    )