from django.test import TestCase
from django.urls import reverse

from accounts.factories import make_job, make_user, make_worker_profile
from jobs.models import Job, Review
from workers.models import WorkerProfile

VERIFIED = WorkerProfile.NIDStatus.VERIFIED


class LandingPageTests(TestCase):
    def test_visitor_sees_the_landing_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landing.html')
        self.assertContains(response, 'Find trusted local workers')

    def test_search_form_uses_the_filter_parameter_names(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'name="district"')
        self.assertContains(response, 'name="skill"')

    def test_logged_in_user_sees_the_dashboard(self):
        self.client.force_login(make_user('emp', 'employer'))
        response = self.client.get(reverse('home'))
        self.assertTemplateNotUsed(response, 'landing.html')
        self.assertContains(response, 'Namaste')

    def test_only_verified_available_workers_are_featured(self):
        make_worker_profile(make_user('verified_vic', 'worker'), nid_status=VERIFIED)
        make_worker_profile(make_user('pending_pat', 'worker'))
        make_worker_profile(make_user('away_amy', 'worker'), nid_status=VERIFIED, is_available=False)
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'verified_vic')
        self.assertNotContains(response, 'pending_pat')
        self.assertNotContains(response, 'away_amy')

    def test_only_reviews_with_a_comment_are_shown(self):
        employer = make_user('emp', 'employer')
        worker = make_user('wrk', 'worker')
        for comment in ('Excellent painter', ''):
            job = make_job(employer, worker, status=Job.Status.COMPLETED)
            Review.objects.create(job=job, reviewer=employer, rating=5, comment=comment)
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Excellent painter')
        self.assertEqual(len(response.context['reviews']), 1)


class VisitorFlowTests(TestCase):
    def test_visitor_is_sent_to_login_for_the_worker_list(self):
        response = self.client.get(reverse('worker_list'))
        expected = reverse('login') + '?next=' + reverse('worker_list')
        self.assertRedirects(response, expected, fetch_redirect_response=False)

    def test_logout_returns_to_the_landing_page(self):
        self.client.force_login(make_user('emp', 'employer'))
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('home'), fetch_redirect_response=False)