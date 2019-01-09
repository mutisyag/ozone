import json
import unittest

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
    SubmissionInfoFactory,
)


class BaseSubmissionInfoTest(TestCase):
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


class TestSubmissionMethods(BaseSubmissionInfoTest):
    """Basic Submission API tests."""

    def test_get(self):
        submission = self.create_submission()
        submission.info.email = "test@example.com"
        submission.info.save()

        headers = self.get_authorization_header(
            self.secretariat_user, password="qwe123qwe"
        )
        resp = self.client.get(
            reverse(
                "core:submission-submission-info-detail",
                kwargs={
                    "submission_pk": submission.pk, "pk": submission.info.pk
                }
            ),
            format="json",
            **headers,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["email"], "test@example.com")

    def test_put(self):
        submission = self.create_submission()

        data = {
            'country': 'Romania',
            'date': None,
            'designation': '',
            'email': "test@example.com",
            'fax': '',
            'organization': '',
            'phone': '0000000000',
            'postal_code': '',
            'reporting_channel': '',
            'reporting_officer': ''
        }

        headers = self.get_authorization_header(
            self.secretariat_user, password="qwe123qwe"
        )
        resp = self.client.put(
            reverse(
                "core:submission-submission-info-detail",
                kwargs={
                    "submission_pk": submission.pk, "pk": submission.info.pk
                }
            ),
            json.dumps(data),
            "application/json",
            format="json",
            **headers,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["email"], "test@example.com")

    @unittest.skip("Currently failing?!")
    def test_put_immutable_state(self):
        submission = self.create_submission()
        submission._current_state = "finalized"
        submission.save()

        data = {
            'country': 'Romania',
            'date': None,
            'designation': '',
            'email': "test@example.com",
            'fax': '',
            'organization': '',
            'phone': '0000000000',
            'postal_code': '',
            'reporting_channel': '',
            'reporting_officer': ''
        }
        headers = self.get_authorization_header(
            self.secretariat_user, password="qwe123qwe"
        )
        resp = self.client.put(
            reverse(
                "core:submission-submission-info-detail",
                kwargs={
                    "submission_pk": submission.pk, "pk": submission.info.pk
                }
            ),
            json.dumps(data),
            "application/json",
            format="json",
            **headers,
        )
        self.assertEqual(resp.status_code, 422)
