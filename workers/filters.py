import django_filters
from django import forms

from .models import WorkerProfile, District, Municipality, Skill

class WorkerFilter(django_filters.FilterSet):
    district = django_filters.ModelChoiceFilter(
        field_name='municipality__district',
        queryset=District.objects.all(),
        empty_label='All districts',
    )
    municipality = django_filters.ModelChoiceFilter(
        queryset=Municipality.objects.select_related('district'),
        empty_label='All municipalities',
    )
    ward_no = django_filters.NumberFilter(label='Ward no.')
    skill = django_filters.ModelChoiceFilter(
        field_name='skills',
        queryset=Skill.objects.all(),
        empty_label='Any skill',
    )
    max_rate = django_filters.NumberFilter(
        field_name='daily_rate',
        lookup_expr='lte',
        label='Max daily rate (Rs.)',
    )

    verified_only = django_filters.BooleanFilter(
        method='filter_verified',
        label='Verified workers only',
        widget=forms.CheckboxInput,
    )

    class Meta:
        model = WorkerProfile
        fields = []

    def filter_verified(self, queryset, name, value):
        if value:
            return queryset.filter(nid_status=WorkerProfile.NIDStatus.VERIFIED)
        return queryset   