from django import forms
from .models import WorkerProfile


class WorkerProfileForm(forms.ModelForm):
    class Meta:
        model = WorkerProfile
        fields = ('skills', 'daily_rate', 'municipality', 'ward_no', 'nid_number', 'nid_photo')
        widgets = {
            'skills': forms.CheckboxSelectMultiple(),
        }