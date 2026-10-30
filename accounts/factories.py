#It is a helper file for testinf data and app.

from itertools import count

from django.contrib.auth import get_user_model

from jobs.models import Job
from workers.models import WorkerProfile

_phone_numbers = count(9800000001)
TEST_PASSWORD = "testpass123"


def make_user(username, role):
    User = get_user_model()
    return User.objects.create_user(
        username=username,
        password=TEST_PASSWORD,
        role=role,
        phone=str(next(_phone_numbers)),
    )


def make_worker_profile(user, **extra):
    values = {"daily_rate": 1000, "ward_no": 1}
    values.update(extra)
    return WorkerProfile.objects.create(user=user, **values)


def make_job(employer, worker, status=Job.Status.REQUESTED, wage=3000):
    return Job.objects.create(
        employer=employer,
        worker=worker,
        description="Test job",
        agreed_wage=wage,
        status=status,
    )