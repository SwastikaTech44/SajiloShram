from django.test import TestCase
from django.urls import reverse

from accounts.factories import make_job, make_user
from jobs.models import Job, Review


class JobStateMachineTests(TestCase):
    def setUp(self):
        self.employer = make_user("emp", "employer")
        self.worker = make_user("wrk", "worker")

    def test_payment_step_cannot_be_skipped(self):
        job = make_job(self.employer, self.worker)
        self.assertFalse(job.can_move_to(Job.Status.COMPLETED))
        with self.assertRaises(ValueError):
            job.move_to(Job.Status.COMPLETED)
        job.refresh_from_db()
        self.assertEqual(job.status, Job.Status.REQUESTED)

    def test_allowed_move_works(self):
        job = make_job(self.employer, self.worker)
        job.move_to(Job.Status.ACCEPTED)
        job.refresh_from_db()
        self.assertEqual(job.status, Job.Status.ACCEPTED)

    def test_declined_job_is_final(self):
        job = make_job(self.employer, self.worker, status=Job.Status.DECLINED)
        self.assertFalse(job.can_move_to(Job.Status.ACCEPTED))


class RespondJobViewTests(TestCase):
    def setUp(self):
        self.employer = make_user("emp", "employer")
        self.worker = make_user("wrk", "worker")
        self.job = make_job(self.employer, self.worker)
        self.url = reverse("respond_job", args=[self.job.pk])

    def test_worker_can_accept(self):
        self.client.force_login(self.worker)
        self.client.post(self.url, {"action": "accept"})
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, Job.Status.ACCEPTED)

    def test_employer_cannot_respond_for_the_worker(self):
        self.client.force_login(self.employer)
        response = self.client.post(self.url, {"action": "accept"})
        self.job.refresh_from_db()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.job.status, Job.Status.REQUESTED)


class ReviewTests(TestCase):
    def setUp(self):
        self.employer = make_user("emp", "employer")
        self.worker = make_user("wrk", "worker")
        self.job = make_job(self.employer, self.worker, status=Job.Status.COMPLETED)
        self.url = reverse("review_job", args=[self.job.pk])

    def test_employer_can_review_a_completed_job(self):
        self.client.force_login(self.employer)
        self.client.post(self.url, {"rating": 5, "comment": "Great work"})
        review = Review.objects.get(job=self.job)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.reviewer, self.employer)

    def test_cannot_review_an_unfinished_job(self):
        self.job.status = Job.Status.FUNDED
        self.job.save()
        self.client.force_login(self.employer)
        self.client.post(self.url, {"rating": 5, "comment": "Too early"})
        self.assertEqual(Review.objects.count(), 0)

    def test_second_review_is_refused(self):
        self.client.force_login(self.employer)
        self.client.post(self.url, {"rating": 5, "comment": "First"})
        self.client.post(self.url, {"rating": 1, "comment": "Second"})
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.get().rating, 5)

    def test_worker_cannot_review_their_own_job(self):
        self.client.force_login(self.worker)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_rating_outside_the_range_is_rejected(self):
        self.client.force_login(self.employer)
        self.client.post(self.url, {"rating": 9, "comment": "Hacked"})
        self.assertEqual(Review.objects.count(), 0)