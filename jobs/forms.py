from django import forms
from .models import Job, Review
from django.utils import timezone

AGREEMENT_WIDGETS = {
    "start_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
    "terms": forms.Textarea(attrs={"rows": 3}),
}
AGREEMENT_LABELS = {
    "start_date": "Start date",
    "work_location": "Work location",
    "terms": "Extra terms (optional)",
}

class AgreementFieldsMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["start_date"].required = True
        self.fields["work_location"].required = True

    def clean_start_date(self):
        start = self.cleaned_data["start_date"]
        if start < timezone.localdate():
            raise forms.ValidationError("The start date cannot be in the past.")
        return start

class JobForm(AgreementFieldsMixin, forms.ModelForm):
    class Meta:
        model = Job
        fields = ("worker", "description", "agreed_wage", "start_date", "work_location", "terms")
        widgets = AGREEMENT_WIDGETS
        labels = AGREEMENT_LABELS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['worker'].queryset = self.fields['worker'].queryset.filter(role='worker')

class HireRequestForm(AgreementFieldsMixin, forms.ModelForm):
    class Meta:
        model = Job
        fields = ["description", "agreed_wage", "start_date", "work_location", "terms"]
        widgets = AGREEMENT_WIDGETS
        labels = AGREEMENT_LABELS
        
class ReviewForm(forms.ModelForm):
    rating = forms.TypedChoiceField(
        choices=[
            ("", "Select a rating"),
            (5, "5 - Excellent"),
            (4, "4 - Good"),
            (3, "3 - Okay"),
            (2, "2 - Poor"),
            (1, "1 - Very poor"),
        ],
        coerce=int,
    )

    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {"comment": forms.Textarea(attrs={"rows": 4})}        