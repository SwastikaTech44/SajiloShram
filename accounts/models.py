#It is component in a system that handles user accounts, authentication, and access control

from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    class Role(models.TextChoices):
        WORKER = 'worker', 'Worker'
        EMPLOYER = 'employer', 'Employer'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.EMPLOYER)
    phone = models.CharField(max_length=15, unique=True)

    REQUIRED_FIELDS = ['email', 'phone']

    def __str__(self):
        return f"{self.username} ({self.role})"


# models.py files (like the User model I wrote) are just Python descriptions of what I want my database tables to look like. PostgreSQL doesn't understand Python — it only understands SQL. makemigrations is the translator that bridges this gap.
