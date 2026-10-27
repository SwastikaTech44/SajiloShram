from django.conf import settings
from django.db import models

class Job(models.Model):
    class Status(models.TextChoices):
        REQUESTED = 'requested', 'Requested'
        ACCEPTED = 'accepted', 'Accepted'
        DECLINED = 'declined', 'Declined'
        FUNDED = 'funded', 'Funded'
        WORK_DONE = 'work_done', 'Work Done'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    ALLOWED_TRANSITIONS = {
        Status.REQUESTED: [Status.ACCEPTED, Status.DECLINED, Status.CANCELLED],
        Status.ACCEPTED: [Status.FUNDED, Status.CANCELLED],
        Status.FUNDED: [Status.WORK_DONE],
        Status.WORK_DONE: [Status.COMPLETED],
    }

    employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='jobs_posted')
    worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='jobs_taken')
    description = models.TextField()
    agreed_wage = models.PositiveIntegerField(help_text='Agreed wage in NPR')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.worker} for {self.employer} - {self.status}"

    def can_move_to(self, new_status):
        return new_status in self.ALLOWED_TRANSITIONS.get(self.status, [])

    def move_to(self, new_status):
        if not self.can_move_to(new_status):
            raise ValueError(f"Cannot go from {self.status} to {new_status}.")
        self.status = new_status
        self.save(update_fields=["status", "updated_at"])


class Review(models.Model):
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name='review')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.job} - {self.rating}★"        