from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from accounts.factories import TEST_PASSWORD, make_job, make_user, make_worker_profile
from workers.models import WorkerProfile


class WorkerApiTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.employer = make_user('emp', 'employer')
        self.verified = make_worker_profile(
            make_user('v', 'worker'),
            nid_status=WorkerProfile.NIDStatus.VERIFIED,
            nid_number='1234567890',
        )
        self.unverified = make_worker_profile(make_user('u', 'worker'))

    def test_anonymous_request_is_refused(self):
        response = self.api.get(reverse('api-worker-list'))
        self.assertIn(response.status_code, (401, 403))

    def test_token_login_returns_a_working_token(self):
        response = self.api.post(
            reverse('api-token'), {'username': 'emp', 'password': TEST_PASSWORD}
        )
        self.assertEqual(response.status_code, 200)
        key = response.json()['token']
        self.assertTrue(Token.objects.filter(user=self.employer, key=key).exists())

        self.api.credentials(HTTP_AUTHORIZATION='Token ' + key)
        listing = self.api.get(reverse('api-worker-list'))
        self.assertEqual(listing.status_code, 200)

    def test_worker_list_never_exposes_nid_or_phone(self):
        self.api.force_authenticate(self.employer)
        response = self.api.get(reverse('api-worker-list'))
        self.assertEqual(response.status_code, 200)
        text = response.content.decode()
        for secret in ('1234567890', 'nid_number', 'nid_photo', 'phone'):
            self.assertNotIn(secret, text)

    def test_verified_only_filter_works_on_the_api(self):
        self.api.force_authenticate(self.employer)
        response = self.api.get(reverse('api-worker-list'), {'verified_only': 'true'})
        ids = [item['id'] for item in response.json()['results']]
        self.assertEqual(ids, [self.verified.pk])


class JobApiTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.employer = make_user('emp', 'employer')
        self.worker = make_user('wrk', 'worker')
        self.mine = make_job(self.employer, self.worker)
        self.theirs = make_job(make_user('emp2', 'employer'), make_user('wrk2', 'worker'))

    def test_user_sees_only_their_own_jobs(self):
        self.api.force_authenticate(self.employer)
        response = self.api.get(reverse('api-job-list'))
        ids = [item['id'] for item in response.json()['results']]
        self.assertEqual(ids, [self.mine.pk])

    def test_other_users_job_is_not_found(self):
        self.api.force_authenticate(self.employer)
        response = self.api.get(reverse('api-job-detail', args=[self.theirs.pk]))
        self.assertEqual(response.status_code, 404)

    def test_api_is_read_only(self):
        self.api.force_authenticate(self.employer)
        response = self.api.post(reverse('api-job-list'), {'description': 'x'})
        self.assertEqual(response.status_code, 405)