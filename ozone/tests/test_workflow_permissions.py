from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import Argon2PasswordHasher

from .factories import (
    PartyFactory,
    ReporterUserFactory,
    SecretariatUserFactory,
    SubmissionFactory
)


User = get_user_model()


class DefaultWorkflowPermissionsTests(TestCase):

    def setUp(self):
        super().setUp()
        self.hash_alg = Argon2PasswordHasher()
        self.secretariat_user = SecretariatUserFactory(
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        self.reporter = ReporterUserFactory(
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )

    def get_authorization_header(self, username, password):
        resp = self.client.post(reverse("core:auth-token-list"), {
            "username": username,
            "password": password,
        }, format="json")
        return {
            'HTTP_AUTHORIZATION': 'Token ' + resp.data['token'],
        }

    def test_submit_secretariat_owner(self):
        """
        Testing `submit` transition using a secretariat user for a submission
        created by the same secretariat user.
        Expected result: 200.
        """

        party = PartyFactory()
        submission = SubmissionFactory(
            party=party,
            _workflow_class='default',
            created_by=self.secretariat_user,
            last_edited_by=self.secretariat_user,
            _current_state='data_entry'
        )
        headers = self.get_authorization_header(self.secretariat_user.username, 'qwe123qwe')
        resp = self.client.post(
            reverse("core:submission-call-transition", kwargs={'pk': submission.pk}),
            {"transition": "submit"},
            **headers
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'submitted')

    def test_submit_secretariat_not_owner(self):
        """
        Testing `submit` transition using a party reporter user for a submission
        created by a secretariat user.
        Expected result: 403 Forbidden.
        """

        party = PartyFactory()
        submission = SubmissionFactory(
            party=party,
            _workflow_class='default',
            created_by=self.reporter,
            last_edited_by=self.reporter,
            _current_state='data_entry'
        )
        headers = self.get_authorization_header(self.reporter.username, 'qwe123qwe')
        resp = self.client.post(
            reverse("core:submission-call-transition", kwargs={'pk': submission.pk}),
            {"transition": "submit"},
            **headers
        )
        self.assertEqual(resp.status_code, 403)

    def test_submit_same_party(self):
        """
        Testing `submit` transition using a party reporter user for a submission
        created by another user from the same party.
        Expected result: 200.
        """

        party = PartyFactory()
        self.reporter.party = party
        self.reporter.save()
        submission = SubmissionFactory(
            party=party,
            _workflow_class='default',
            created_by=self.reporter,
            last_edited_by=self.reporter,
            _current_state='data_entry'
        )
        reporter_same_party = ReporterUserFactory(
            party=party,
            username='reporter_same_party',
            email='reporter_same_party@example.com',
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        headers = self.get_authorization_header(reporter_same_party.username, 'qwe123qwe')
        resp = self.client.post(
            reverse("core:submission-call-transition", kwargs={'pk': submission.pk}),
            {"transition": "submit", "party": party.pk},
            **headers
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'submitted')

    def test_process(self):
        pass

    def test_recall(self):
        pass

    def test_unrecall(self):
        pass

    def test_finalize(self):
        pass


class AcceleratedWorkflowTests(TestCase):
    pass