from datetime import datetime

from django.urls import reverse
from django.contrib.auth.hashers import Argon2PasswordHasher

from ozone.core.models import Submission, SubmissionInfo

from .base import BaseTests
from .factories import (
    PartyFactory,
    PartyHistoryFactory,
    RegionFactory,
    ReportingPeriodFactory,
    ObligationFactory,
    ReportingChannelFactory,
    LanguageEnFactory,
    SecretariatUserFactory,
    SubmissionFactory,
    SubregionFactory,
    SubstanceFactory,
    AnotherPartyFactory,
)

LINKS_ART7 = (
    'article7questionnaire_url', 'article7questionnaire',
    'article7destructions_url', 'article7productions_url',
    'article7exports_url', 'article7imports_url',
    'article7nonpartytrades_url', 'article7emissions_url',
)
LINKS_HAT = (
    'hat_productions_url', 'hat_imports_url',
)
LINKS_ESSENCRIT = ()
LINKS_OTHER = (
    'data_others_url',
)
ALL_LINKS = LINKS_ART7 + LINKS_HAT + LINKS_ESSENCRIT + LINKS_OTHER


class BaseSubmissionTest(BaseTests):
    _form_type = "art7"

    def setUp(self):
        super().setUp()
        self.workflow_class = "default"

        self.region = RegionFactory.create()
        self.period = ReportingPeriodFactory.create(name="Some period")
        self.obligation = ObligationFactory.create(_form_type=self._form_type)
        self.subregion = SubregionFactory.create(region=self.region)
        self.party = PartyFactory(subregion=self.subregion)
        self.another_party = AnotherPartyFactory(subregion=self.subregion)
        self.language = LanguageEnFactory()

        PartyHistoryFactory(party=self.party, reporting_period=self.period)

        hash_alg = Argon2PasswordHasher()
        self.secretariat_user = SecretariatUserFactory(
            language=self.language,
            password=hash_alg.encode(password="qwe123qwe", salt="123salt123")
        )
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')

        self.substance = SubstanceFactory()
        ReportingChannelFactory()

    def create_submission(self, **kwargs):
        submission = SubmissionFactory.create(
            party=self.party,
            obligation=self.obligation,
            created_by=self.secretariat_user,
            last_edited_by=self.secretariat_user,
            **kwargs,
        )
        return submission


class TestSubmissionMethods(BaseSubmissionTest):
    """Basic Submission API tests."""

    links_data = LINKS_ART7

    def test_create(self):
        data = {
            "reporting_period": self.period.id,
            "party": self.party.id,
            "obligation": self.obligation.id,
        }
        result = self.client.post(
            reverse("core:submission-list"),
            data,
        )
        self.assertEqual(result.status_code, 201, result.json())
        submission = Submission.objects.get(pk=result.json()["id"])
        self.assertEqual(submission.obligation_id, self.obligation.id)
        self.assertEqual(submission.reporting_period_id, self.period.id)
        self.assertEqual(submission.party_id, self.party.id)

    def test_create_auto_info(self):
        """A SubmissionInfo should be automatically generated for
        a new submission.
        """
        data = {
            "reporting_period": self.period.id,
            "party": self.party.id,
            "obligation": self.obligation.id,
        }
        result = self.client.post(
            reverse("core:submission-list"),
            data,
        )
        self.assertEqual(result.status_code, 201, result.json())
        submission = Submission.objects.get(pk=result.json()["id"])
        self.assertTrue(submission.info)

    def test_get(self):
        submission = self.create_submission()

        result = self.client.get(
            reverse("core:submission-detail", kwargs={"pk": submission.id}),
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()['party'], self.party.id)

    def test_get_check_urls(self):
        submission = self.create_submission()

        result = self.client.get(
            reverse("core:submission-detail", kwargs={"pk": submission.id}),
        )
        self.assertEqual(result.status_code, 200)

        for link in ALL_LINKS:
            with self.subTest("Check link %s" % link):
                if link in self.links_data:
                    self.assertIn(link, result.json())
                else:
                    self.assertNotIn(link, result.json())

    def test_delete(self):
        submission = self.create_submission()

        result = self.client.delete(
            reverse("core:submission-detail", kwargs={"pk": submission.id}),
        )
        self.assertEqual(result.status_code, 204)
        with self.assertRaises(Submission.DoesNotExist):
            Submission.objects.get(pk=submission.id)

        with self.assertRaises(SubmissionInfo.DoesNotExist):
            SubmissionInfo.objects.get(submission__id=submission.id)

    def test_update(self):
        submission = self.create_submission()

        result = self.client.put(
            reverse("core:submission-detail", kwargs={"pk": submission.id}),
            {"party": self.another_party.id},
        )
        self.assertEqual(result.status_code, 200, result.json())
        submission = Submission.objects.get(pk=submission.id)
        self.assertEqual(submission.party, self.another_party)

    def test_list(self):
        submission = self.create_submission()

        result = self.client.get(
            reverse("core:submission-list"),
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.json()), 1)
        self.assertEqual(result.json()[0]["id"], submission.id)

    def test_list_all_versions(self):
        submission = self.create_submission()
        submission.call_transition("submit", self.secretariat_user)
        submission.clone(self.secretariat_user)

        result = self.client.get(
            reverse("core:submission-list"),
            {"ordering": "-updated_at"},
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.json()), 2)
        self.assertEqual(result.json()[0]['version'], 2)
        self.assertEqual(result.json()[1]['version'], 1)

    def test_list_current_only(self):
        submission = self.create_submission()
        submission.call_transition("submit", self.secretariat_user)
        clone = submission.clone(self.secretariat_user)
        clone.info.reporting_officer = 'Test Officer'
        clone.info.postal_address = 'Test Address'
        clone.info.email = 'test@officer.net'
        clone.info.save()
        clone.submitted_at = datetime.strptime('2019-01-01', "%Y-%m-%d")
        clone.save()
        # This should make the first one superseded
        clone.call_transition("submit", self.secretariat_user)

        result = self.client.get(
            reverse("core:submission-list"),
            {"ordering": "-updated_at", "is_superseded": False},
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.json()), 1)
        self.assertEqual(result.json()[0]['version'], 2)

    def test_list_superseded_only(self):
        submission = self.create_submission()
        submission.call_transition("submit", self.secretariat_user)
        clone = submission.clone(self.secretariat_user)
        clone.info.reporting_officer = 'Test Officer'
        clone.info.postal_address = 'Test Address'
        clone.info.email = 'test@officer.net'
        clone.info.save()
        clone.submitted_at = datetime.strptime('2019-01-01', "%Y-%m-%d")
        clone.save()
        # This should make the first one superseded
        clone.call_transition("submit", self.secretariat_user)

        result = self.client.get(
            reverse("core:submission-list"),
            {"ordering": "-updated_at", "is_superseded": True},
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.json()), 1)
        self.assertEqual(result.json()[0]['version'], 1)

    def test_list_paginated(self):
        submission1 = self.create_submission()
        submission2 = self.create_submission(reporting_period=self.period)

        result = self.client.get(
            reverse("core:submission-list"),
            {"page": 1, "page_size": 1, "ordering": "reporting_period"},
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.json()['results']), 1)
        self.assertEqual(result.json()['results'][0]["id"], submission2.id)

        result = self.client.get(
            reverse("core:submission-list"),
            {"page": 2, "page_size": 1, "ordering": "reporting_period"},
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.json()['results']), 1)
        self.assertEqual(result.json()['results'][0]["id"], submission1.id)

    def test_clone(self):
        submission = self.create_submission()
        submission._current_state = "finalized"
        submission.save()

        result = self.client.post(
            reverse(
                "core:submission-clone",
                kwargs={"pk": submission.pk},
            ),
        )
        self.assertEqual(result.status_code, 200, result.json())
        new_id = result.json()['url'].split("/")[-2]

        new_submission = Submission.objects.get(pk=new_id)
        self.assertEqual(new_submission.party, submission.party)
        self.assertEqual(new_submission.obligation, submission.obligation)
        self.assertEqual(new_submission.reporting_period, submission.reporting_period)

    def test_clone_versions(self):
        submission = self.create_submission()
        submission.call_transition("submit", self.secretariat_user)
        submission.save()
        new_submission = submission.clone(self.secretariat_user)

        result = self.client.get(
            reverse(
                "core:submission-versions",
                kwargs={"pk": new_submission.pk},
            ),
            {"ordering": "-version"},
        )
        self.assertEqual(result.status_code, 200, result.json())
        self.assertEqual(result.json()[0]['version'], 2)
        self.assertEqual(result.json()[1]['version'], 1)

    def test_history(self):
        submission = self.create_submission()
        submission.call_transition("submit", self.secretariat_user)
        submission.save()
        for obj in submission.history.all():
            obj.history_user = self.secretariat_user
            obj.save()

        result = self.client.get(
            reverse("core:submission-history", kwargs={"pk": submission.id}),
        )
        self.assertEqual(result.status_code, 200)
        submission.refresh_from_db()
        # Apparently there should be 4 history items; the extra one appears
        # because SubmissionFactory.create() actually does change attributes
        # on the submission to make "Submit" available!
        self.assertEqual(len(result.json()), 5)
        self.assertEqual(result.json()[-1]['current_state'], 'data_entry')
        self.assertEqual(result.json()[0]['current_state'], 'submitted')


class HATSubmissionMethods(TestSubmissionMethods):
    _form_type = "hat"
    links_data = LINKS_HAT


class EssenCritSubmissionMethods(TestSubmissionMethods):
    _form_type = "essencrit"
    links_data = LINKS_ESSENCRIT


class OtherSubmissionMethods(TestSubmissionMethods):
    _form_type = "other"
    links_data = LINKS_OTHER

    def test_clone(self):
        """
        Overriding method from main class, as form_type "other" does not
        allow cloning
        """
        submission = self.create_submission()
        submission._current_state = "finalized"
        submission.save()

        result = self.client.post(
            reverse(
                "core:submission-clone",
                kwargs={"pk": submission.pk},
            ),
        )
        self.assertEqual(result.status_code, 422, result.json())

    def test_clone_versions(self):
        """Cloning not allowed for these submissions"""
        pass

    def test_list_all_versions(self):
        """Cloning not allowed for these submissions"""
        pass

    def test_list_current_only(self):
        """Cloning not allowed for these submissions"""
        pass

    def test_list_superseded_only(self):
        """Cloning not allowed for these submissions"""
        pass
