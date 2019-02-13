import json

from django.urls import reverse
from django.contrib.auth.hashers import Argon2PasswordHasher

from .base import BaseTests
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


class BaseSubmissionInfoTest(BaseTests):
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
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')

        self.substance = SubstanceFactory()
        ReportingChannelFactory()

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

        resp = self.client.get(
            reverse(
                "core:submission-submission-info-detail",
                kwargs={
                    "submission_pk": submission.pk, "pk": submission.info.pk
                }
            ),
            format="json",
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
            'organization': '',
            'phone': '0000000000',
            'postal_address': '',
            'postal_code': '',
            'reporting_officer': ''
        }

        resp = self.client.put(
            reverse(
                "core:submission-submission-info-detail",
                kwargs={
                    "submission_pk": submission.pk, "pk": submission.info.pk
                }
            ),
            data,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["email"], "test@example.com")

    def test_put_immutable_state(self):
        submission = self.create_submission()
        submission._current_state = "finalized"
        submission.save()

        data = {
            'country': 'Romania',
            'date': None,
            'designation': '',
            'email': "test@example.com",
            'organization': '',
            'phone': '0000000000',
            'postal_address': '',
            'postal_code': '',
            'reporting_officer': ''
        }
        resp = self.client.put(
            reverse(
                "core:submission-submission-info-detail",
                kwargs={
                    "submission_pk": submission.pk, "pk": submission.info.pk
                }
            ),
            data,
        )
        self.assertEqual(resp.status_code, 422)
