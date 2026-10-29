from django import forms
from django.core.files.uploadedfile import UploadedFile
from .models import WorkerProfile


class WorkerProfileForm(forms.ModelForm):
    class Meta:
        model = WorkerProfile
        fields = ('skills', 'daily_rate', 'municipality', 'ward_no', 'nid_number', 'nid_photo')
        widgets = {
            'skills': forms.CheckboxSelectMultiple(),
        }

NID_LENGTH = 10
MAX_PHOTO_MB = 2


class NIDSubmissionForm(forms.ModelForm):
    class Meta:
        model = WorkerProfile
        fields = ["nid_number", "nid_photo"]
        labels = {
            "nid_number": "NID number",
            "nid_photo": "NID photo",
        }
        widgets = {
            "nid_photo": forms.FileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nid_number"].required = True
        self.fields["nid_photo"].required = True

    def clean_nid_number(self):
        raw = self.cleaned_data["nid_number"]
        digits = raw.replace("-", "").replace(" ", "")
        if not (digits.isascii() and digits.isdigit() and len(digits) == NID_LENGTH):
            raise forms.ValidationError(f"Enter a {NID_LENGTH}-digit NID number.")

        taken = (
            WorkerProfile.objects.filter(nid_number=digits)
            .exclude(pk=self.instance.pk)
            .exists()
        )
        if taken:
            raise forms.ValidationError("This NID number cannot be used. Please contact support.")
        return digits

    def clean_nid_photo(self):
        photo = self.cleaned_data["nid_photo"]
        if photo and photo.size > MAX_PHOTO_MB * 1024 * 1024:
            raise forms.ValidationError(f"The photo must be smaller than {MAX_PHOTO_MB} MB.")
        return photo