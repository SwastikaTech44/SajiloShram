from django.test import TestCase
from django.urls import reverse

from accounts.factories import make_user, make_worker_profile
from workers.filters import WorkerFilter
from workers.forms import NIDSubmissionForm
from workers.models import WorkerProfile


class NIDFormTests(TestCase):
    def setUp(self):
        self.profile = make_worker_profile(make_user("w1", "worker"))

    def test_short_number_is_rejected(self):
        form = NIDSubmissionForm({"nid_number": "12345"}, instance=self.profile)
        self.assertFalse(form.is_valid())
        self.assertIn("nid_number", form.errors)

    def test_dashes_and_spaces_are_cleaned(self):
        form = NIDSubmissionForm({"nid_number": "123-456 7890"}, instance=self.profile)
        form.is_valid()
        self.assertNotIn("nid_number", form.errors)
        self.assertEqual(form.cleaned_data["nid_number"], "1234567890")

    def test_number_used_by_another_worker_is_rejected(self):
        make_worker_profile(make_user("w2", "worker"), nid_number="1234567890")
        form = NIDSubmissionForm({"nid_number": "123-456-7890"}, instance=self.profile)
        self.assertIn("nid_number", form.errors)

    def test_worker_can_resubmit_their_own_number(self):
        self.profile.nid_number = "1234567890"
        self.profile.save()
        form = NIDSubmissionForm({"nid_number": "1234567890"}, instance=self.profile)
        form.is_valid()
        self.assertNotIn("nid_number", form.errors)


class NIDViewTests(TestCase):
    def test_employer_cannot_open_the_nid_page(self):
        employer = make_user("emp", "employer")
        self.client.force_login(employer)
        response = self.client.get(reverse("verify_nid"))
        self.assertRedirects(response, reverse("dashboard"), fetch_redirect_response=False)


class VerifiedFilterTests(TestCase):
    def setUp(self):
        self.verified = make_worker_profile(
            make_user("v", "worker"), nid_status=WorkerProfile.NIDStatus.VERIFIED
        )
        self.unverified = make_worker_profile(make_user("u", "worker"))

    def test_verified_only_hides_unverified_workers(self):
        result = WorkerFilter(
            {"verified_only": "on"}, queryset=WorkerProfile.objects.all()
        ).qs
        self.assertEqual(list(result), [self.verified])

    def test_without_the_checkbox_everyone_is_listed(self):
        result = WorkerFilter({}, queryset=WorkerProfile.objects.all()).qs
        self.assertEqual(result.count(), 2)

