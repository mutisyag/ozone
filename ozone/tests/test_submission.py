import json

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import Argon2PasswordHasher

from ozone.core.models import Submission, SubmissionInfo

from .factories import (
    PartyFactory,
    RegionFactory,
    ReportingPeriodFactory,
    ObligationFactory,
    ReporterUserFactory,
    ReportingChannelFactory,
    SecretariatUserFactory,
    SubmissionFactory,
    SubregionFactory,
    SubstanceFactory,
    AnotherPartyFactory,
)


class BaseSubmissionTest(TestCase):
    def setUp(self):
        super().setUp()
        self.workflow_class = "default"

        self.region = RegionFactory.create()
        self.period = ReportingPeriodFactory.create(name="Some period")
        self.obligation = ObligationFactory.create(name="Some obligation")
        self.subregion = SubregionFactory.create(region=self.region)
        self.party = PartyFactory(subregion=self.subregion)
        self.another_party = AnotherPartyFactory(subregion=self.subregion)

        hash_alg = Argon2PasswordHasher()
        self.secretariat_user = SecretariatUserFactory(
            password=hash_alg.encode(password="qwe123qwe", salt="123salt123")
        )
        self.party_user = ReporterUserFactory(
            party=self.party,
            password=hash_alg.encode(password="qwe123qwe", salt="123salt123"),
        )
        self.substance = SubstanceFactory()
        ReportingChannelFactory()

    def get_authorization_header(self, username, password):
        resp = self.client.post(
            reverse("core:auth-token-list"),
            {"username": username, "password": password},
            format="json",
        )
        return {"HTTP_AUTHORIZATION": "Token " + resp.data["token"]}

    def create_submission(self, **kwargs):
        submission = SubmissionFactory.create(
            party=self.party,
            created_by=self.secretariat_user,
            last_edited_by=self.secretariat_user,
            **kwargs,
        )
        return submission


class TestSubmissionMethods(BaseSubmissionTest):
    """Basic Submission API tests."""
    def test_create(self):
        headers = self.get_authorization_header(
            self.secretariat_user.username, "qwe123qwe"
        )

        data = {
            "reporting_period": self.period.id,
            "party": self.party.id,
            "obligation": self.obligation.id,
        }
        result = self.client.post(
            reverse("core:submission-list"),
            json.dumps(data),
            "application/json",
            format="json",
            **headers,
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
        headers = self.get_authorization_header(
            self.secretariat_user.username, "qwe123qwe"
        )

        data = {
            "reporting_period": self.period.id,
            "party": self.party.id,
            "obligation": self.obligation.id,
        }
        result = self.client.post(
            reverse("core:submission-list"),
            json.dumps(data),
            "application/json",
            format="json",
            **headers,
        )
        self.assertEqual(result.status_code, 201, result.json())
        submission = Submission.objects.get(pk=result.json()["id"])
        self.assertTrue(submission.info)

    def test_get(self):
        headers = self.get_authorization_header(
            self.secretariat_user.username, "qwe123qwe"
        )
        submission = self.create_submission()

        result = self.client.get(
            reverse("core:submission-detail", kwargs={"pk": submission.id}),
            format="json",
            **headers,
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()['party'], self.party.id)

    def test_delete(self):
        headers = self.get_authorization_header(
            self.secretariat_user.username, "qwe123qwe"
        )
        submission = self.create_submission()

        result = self.client.delete(
            reverse("core:submission-detail", kwargs={"pk": submission.id}),
            format="json",
            **headers,
        )
        self.assertEqual(result.status_code, 204)
        with self.assertRaises(Submission.DoesNotExist):
            Submission.objects.get(pk=submission.id)

        with self.assertRaises(SubmissionInfo.DoesNotExist):
            SubmissionInfo.objects.get(submission__id=submission.id)

    def test_update(self):
        headers = self.get_authorization_header(
            self.secretariat_user.username, "qwe123qwe"
        )
        submission = self.create_submission()

        result = self.client.put(
            reverse("core:submission-detail", kwargs={"pk": submission.id}),
            json.dumps({"party": self.another_party.id}),
            "application/json",
            format="json",
            **headers,
        )
        self.assertEqual(result.status_code, 200, result.json())
        submission = Submission.objects.get(pk=submission.id)
        self.assertEqual(submission.party, self.another_party)

    def test_list(self):
        headers = self.get_authorization_header(
            self.secretariat_user.username, "qwe123qwe"
        )
        submission = self.create_submission()

        result = self.client.get(
            reverse("core:submission-list"),
            format="json",
            **headers,
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.json()['results']), 1)
        self.assertEqual(result.json()['results'][0]["id"], submission.id)

    def test_list_paginated(self):
        headers = self.get_authorization_header(
            self.secretariat_user.username, "qwe123qwe"
        )
        submission1 = self.create_submission()
        submission2 = self.create_submission(
            obligation=self.obligation, reporting_period=self.period,
        )

        result = self.client.get(
            reverse("core:submission-list"),
            {"page": 1, "page_size": 1, "ordering": "period"},
            format="json",
            **headers,
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.json()['results']), 1)
        self.assertEqual(result.json()['results'][0]["id"], submission1.id)

        result = self.client.get(
            reverse("core:submission-list"),
            {"page": 2, "page_size": 1, "ordering": "period"},
            format="json",
            **headers,
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.json()['results']), 1)
        self.assertEqual(result.json()['results'][0]["id"], submission2.id)

    def test_clone(self):
        submission = self.create_submission()
        submission._current_state = "finalized"
        submission.save()

        headers = self.get_authorization_header(self.secretariat_user.username, "qwe123qwe")

        result = self.client.post(
            reverse(
                "core:submission-clone",
                kwargs={"pk": submission.pk},
            ),
            format="json",
            **headers,
        )
        self.assertEqual(result.status_code, 200, result.json())
        new_id = result.json()['url'].split("/")[-2]

        new_submission = Submission.objects.get(pk=new_id)
        self.assertEqual(new_submission.party, submission.party)
        self.assertEqual(new_submission.obligation, submission.obligation)
        self.assertEqual(new_submission.reporting_period, submission.reporting_period)

    def test_history(self):
        submission = self.create_submission()
        submission.call_transition("submit", self.secretariat_user)
        submission.save()
        for obj in submission.history.all():
            obj.history_user = self.secretariat_user
            obj.save()

        headers = self.get_authorization_header(
            self.secretariat_user.username, "qwe123qwe"
        )
        result = self.client.get(
            reverse("core:submission-history", kwargs={"pk": submission.id}),
            format="json",
            **headers,
        )
        self.assertEqual(result.status_code, 200)
        submission.refresh_from_db()
        self.assertEqual(len(result.json()), 5)
        self.assertEqual(result.json()[-1]['current_state'], 'data_entry')
        self.assertEqual(result.json()[0]['current_state'], 'submitted')

