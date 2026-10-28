from django import forms
from .models import Job, Review


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