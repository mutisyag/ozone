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
    Article7QuestionnaireFactory,
)


class BaseQuestionnaireSubmissionTest(TestCase):
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


class TestSubmissionMethods(BaseQuestionnaireSubmissionTest):
    """Basic Submission API tests."""

    def test_get(self):
        submission = self.create_submission()
        art7question = Article7QuestionnaireFactory.create(
            submission=submission, has_imports=True,
        )

        headers = self.get_authorization_header(self.secretariat_user, password="qwe123qwe")
        resp = self.client.get(
            reverse("core:submission-article7-questionnaire-detail",
                    kwargs={"submission_pk": submission.pk, "pk": art7question.pk}),
            format="json",
            **headers,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["has_imports"], True)
        self.assertEqual(resp.json()["has_exports"], False)

    def test_post(self):
        submission = self.create_submission()
        data = {
            'has_destroyed': False,
            'has_emissions': False,
            'has_exports': False,
            'has_imports': True,
            'has_nonparty': False,
            'has_produced': False,
        }
        headers = self.get_authorization_header(self.secretariat_user, password="qwe123qwe")
        resp = self.client.post(
            reverse("core:submission-article7-questionnaire-list",
                    kwargs={"submission_pk": submission.pk}),
            data,
            format="json",
            **headers,
        )
        self.assertEqual(resp.status_code, 201)
        submission.refresh_from_db()
        self.assertEqual(submission.article7questionnaire.has_imports, True)
        self.assertEqual(submission.article7questionnaire.has_exports, False)

    def test_put(self):
        submission = self.create_submission()
        art7question = Article7QuestionnaireFactory.create(
            submission=submission,
        )
        data = {
            'has_destroyed': False,
            'has_emissions': False,
            'has_exports': False,
            'has_imports': True,
            'has_nonparty': False,
            'has_produced': False,
        }
        headers = self.get_authorization_header(self.secretariat_user, password="qwe123qwe")
        resp = self.client.put(
            reverse("core:submission-article7-questionnaire-detail",
                    kwargs={"submission_pk": submission.pk, "pk": art7question.pk}),
            json.dumps(data),
            "application/json",
            format="json",
            **headers,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["has_imports"], True)
        self.assertEqual(resp.json()["has_exports"], False)
