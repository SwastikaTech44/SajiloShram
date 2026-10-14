from django.conf import settings
from django.db import models
from jobs.models import Job


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.PositiveIntegerField(default=0, help_text='Balance in NPR')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s wallet - Rs. {self.balance}"


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        DEPOSIT = 'deposit', 'Deposit (held in escrow)'
        RELEASE = 'release', 'Release to worker'
        REFUND = 'refund', 'Refund to employer'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='transactions')
    amount = models.PositiveIntegerField(help_text='Amount in NPR')
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    gateway_reference = models.CharField(max_length=100, blank=True, help_text='eSewa/Khalti transaction ID')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - Rs. {self.amount} for {self.job}"
