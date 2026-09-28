from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

# Creating models here.

class District(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Municipality(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='municipalities')
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Municipalities'
        unique_together = ('district', 'name')

    def __str__(self):
        return f"{self.name}, {self.district.name}"


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class WorkerProfile(models.Model):
    class NIDStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        VERIFIED = 'verified', 'Verified'
        REJECTED = 'rejected', 'Rejected'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='worker_profile')
    skills = models.ManyToManyField(Skill, related_name='workers')
    daily_rate = models.PositiveIntegerField(help_text='Daily wage in NPR')
    municipality = models.ForeignKey(Municipality, on_delete=models.SET_NULL, null=True)
    ward_no = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(33)]
    )
    is_available = models.BooleanField(default=True)
    audio_intro = models.FileField(upload_to='audio_intros/', blank=True, null=True)
    nid_number = models.CharField(max_length=20, blank=True)
    nid_photo = models.ImageField(upload_to='nid_photos/', blank=True, null=True)
    nid_status = models.CharField(max_length=10, choices=NIDStatus.choices, default=NIDStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.username}"