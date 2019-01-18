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
    Article7QuestionnaireFactory,
)


class BaseQuestionnaireSubmissionTest(BaseTests):
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


class TestSubmissionMethods(BaseQuestionnaireSubmissionTest):
    """Basic Submission API tests."""

    def test_get(self):
        submission = self.create_submission()
        art7question = Article7QuestionnaireFactory.create(
            submission=submission, has_imports=True,
        )
        resp = self.client.get(
            reverse("core:submission-article7-questionnaire-detail",
                    kwargs={"submission_pk": submission.pk, "pk": art7question.pk}),
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
        resp = self.client.post(
            reverse("core:submission-article7-questionnaire-list",
                    kwargs={"submission_pk": submission.pk}),
            data,
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
        resp = self.client.put(
            reverse("core:submission-article7-questionnaire-detail",
                    kwargs={"submission_pk": submission.pk, "pk": art7question.pk}),
            data,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["has_imports"], True)
        self.assertEqual(resp.json()["has_exports"], False)

    def test_put_immutable_state(self):
        submission = self.create_submission()
        art7question = Article7QuestionnaireFactory.create(
            submission=submission,

        )
        submission._current_state = "finalized"
        submission.save()

        data = {
            'has_destroyed': False,
            'has_emissions': False,
            'has_exports': False,
            'has_imports': True,
            'has_nonparty': False,
            'has_produced': False,
        }
        resp = self.client.put(
            reverse("core:submission-article7-questionnaire-detail",
                    kwargs={"submission_pk": submission.pk, "pk": art7question.pk}),
            data,
        )
        self.assertEqual(resp.status_code, 422)
