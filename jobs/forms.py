from django import forms
from .models import Job


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ('worker', 'description', 'agreed_wage')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['worker'].queryset = self.fields['worker'].queryset.filter(role='worker')

class HireRequestForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["description", "agreed_wage"]