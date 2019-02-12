from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import Argon2PasswordHasher

from .base import BaseTests
from .factories import (
    PartyFactory,
    RegionFactory,
    ReportingChannelFactory,
    ReporterUserFactory,
    SecretariatUserFactory,
    SubmissionFactory,
    SubregionFactory,
)

User = get_user_model()


class SubmissionReportingChannelTests(BaseTests):

    def setUp(self):
        super().setUp()
        self.workflow_class = 'base'

        self.region = RegionFactory.create()
        self.subregion = SubregionFactory.create(region=self.region)
        self.party = PartyFactory(subregion=self.subregion)

        hash_alg = Argon2PasswordHasher()
        self.secretariat_user = SecretariatUserFactory(
            password=hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        self.reporter = ReporterUserFactory(
            party=self.party,
            password=hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        ReportingChannelFactory.create(name='Web form')
        ReportingChannelFactory.create(name='API')

    def create_submission(self, owner, current_state='data_entry', previous_state=None):
        submission = SubmissionFactory(
            party=self.party, created_by=owner, last_edited_by=owner
        )
        submission._previous_state = previous_state
        submission._current_state = current_state
        submission.save()
        return submission

    def test_secretartiat_owner(self):
        submission = self.create_submission(owner=self.secretariat_user)
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
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
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['reporting_channel'], 'API')

    def test_secretariat_owner_submitted_submission_and_submission_info(self):
        submission = self.create_submission(
            owner=self.secretariat_user,
            current_state='submitted',
            previous_state='data_entry'
        )
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        data = {
            "reporting_channel": "API",
            "reporting_officer": "test",
            "designation": "test",
            "organization": "test",
            "postal_code": "test",
            "country": "test",
            "phone": "test",
            "email": None,
            "date": None
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

    def test_secretartiat_owner_submitted_submission(self):
        submission = self.create_submission(
            owner=self.secretariat_user,
            current_state='submitted',
            previous_state='data_entry'
        )
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
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
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['reporting_channel'], 'API')

    def test_secretartiat_not_owner(self):
        submission = self.create_submission(owner=self.reporter)
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
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
