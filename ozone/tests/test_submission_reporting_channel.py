from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import Argon2PasswordHasher

from .base import BaseTests
from .factories import (
    PartyFactory,
    RegionFactory,
    ReportingChannelFactory,
    LanguageEnFactory,
    ReporterUserFactory,
    SecretariatUserFactory,
    SubmissionFactory,
    SubregionFactory,
    SubmissionFormatFactory,
)

User = get_user_model()


class SubmissionReportingChannelTests(BaseTests):

    def setUp(self):
        super().setUp()
        self.workflow_class = 'base'

        self.region = RegionFactory.create()
        self.subregion = SubregionFactory.create(region=self.region)
        self.party = PartyFactory(subregion=self.subregion)
        self.language = LanguageEnFactory()

        hash_alg = Argon2PasswordHasher()
        self.secretariat_user = SecretariatUserFactory(
            language=self.language,
            password=hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        self.reporter = ReporterUserFactory(
            language=self.language,
            party=self.party,
            password=hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        ReportingChannelFactory.create(
            name='Web form',
            is_default_party=True,
            is_default_secretariat=False,
            is_default_for_cloning=True
        )
        ReportingChannelFactory.create(
            name='Email',
            is_default_party=False,
            is_default_secretariat=True,
            is_default_for_cloning=False
        )
        ReportingChannelFactory.create(
            name='API',
            is_default_party=False,
            is_default_secretariat=False,
            is_default_for_cloning=False
        )
        SubmissionFormatFactory()

    def create_submission(
        self, owner, current_state='data_entry', previous_state=None
    ):
        submission = SubmissionFactory(
            party=self.party, created_by=owner, last_edited_by=owner
        )
        submission._previous_state = previous_state
        submission._current_state = current_state
        submission.save()
        return submission

    def test_secretariat_owner(self):
        submission = self.create_submission(owner=self.secretariat_user)
        self.client.login(
            username=self.secretariat_user.username, password='qwe123qwe'
        )
        data = {
            "reporting_channel": "API"
        }
        resp = self.client.put(
            reverse(
                "core:submission-submission-info-list",
                kwargs={
                    "submission_pk": submission.pk
                }
            ),
            data
        )
        self.assertEqual(submission.reporting_channel.name, 'Email')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['reporting_channel'], 'API')

    def test_secretariat_owner_finalized_submission_and_submission_info(self):
        submission = self.create_submission(
            owner=self.secretariat_user,
            current_state='finalized',
            previous_state='data_entry'
        )
        self.client.login(
            username=self.secretariat_user.username, password='qwe123qwe'
        )
        data = {
            "reporting_channel": "API",
            "reporting_officer": "test",
            "designation": "test",
            "organization": "test",
            "postal_address": "test",
            "country": "test",
            "phone": "test",
            "email": None,
            "date": None,
            'submission_format': 'A7 Data forms'
        }
        resp = self.client.put(
            reverse(
                "core:submission-submission-info-list",
                kwargs={
                    "submission_pk": submission.pk
                }
            ),
            data
        )
        self.assertEqual(submission.reporting_channel.name, 'Email')
        self.assertEqual(resp.status_code, 422)

    def test_secretariat_owner_finalized_submission(self):
        submission = self.create_submission(
            owner=self.secretariat_user,
            current_state='finalized',
            previous_state='data_entry'
        )
        self.client.login(
            username=self.secretariat_user.username, password='qwe123qwe'
        )
        data = {
            "reporting_channel": "API"
        }
        resp = self.client.put(
            reverse(
                "core:submission-submission-info-list",
                kwargs={
                    "submission_pk": submission.pk
                }
            ),
            data
        )
        self.assertEqual(submission.reporting_channel.name, 'Email')
        self.assertEqual(resp.status_code, 422)

    def test_secretariat_not_owner(self):
        submission = self.create_submission(owner=self.reporter)
        self.client.login(
            username=self.secretariat_user.username, password='qwe123qwe'
        )
        data = {
            "reporting_channel": "API"
        }
        resp = self.client.put(
            reverse(
                "core:submission-submission-info-list",
                kwargs={
                    "submission_pk": submission.pk
                }
            ),
            data
        )
        self.assertEqual(submission.reporting_channel.name, 'Web form')
        self.assertEqual(resp.status_code, 422)
