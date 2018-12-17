from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import Argon2PasswordHasher

from .factories import (
    PartyFactory,
    RegionFactory,
    ReporterUserFactory,
    SecretariatUserFactory,
    SubmissionFactory,
    SubregionFactory,
)


User = get_user_model()


class ClonePermissionsTests(TestCase):

    def setUp(self):
        super().setUp()
        self.hash_alg = Argon2PasswordHasher()
        self.region = RegionFactory.create()
        self.subregion = SubregionFactory.create(region=self.region)

    def get_authorization_header(self, username, password):
        resp = self.client.post(reverse("core:auth-token-list"), {
            "username": username,
            "password": password,
        }, format="json")
        return {
            'HTTP_AUTHORIZATION': 'Token ' + resp.data['token'],
        }

    def test_clone_secretariat(self):
        """
        Testing `clone` action using a secretariat user.
        Expected result: 200.
        """

        party = PartyFactory(subregion=self.subregion)
        secretariat_user = SecretariatUserFactory(
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        submission = SubmissionFactory(
            party=party,
            created_by=secretariat_user,
            last_edited_by=secretariat_user,
        )
        submission._current_state = 'submitted'
        submission.save()
        headers = self.get_authorization_header(secretariat_user.username, 'qwe123qwe')
        resp = self.client.post(
            reverse("core:submission-clone",
                    kwargs={'pk': submission.pk}),
            **headers
        )
        self.assertEqual(resp.status_code, 200)

    def test_clone_same_party(self):
        """
        Testing `clone` action using a party reporter user for a submission
        created by another user from the same party.
        Expected result: 200.
        """

        party = PartyFactory(subregion=self.subregion)
        reporter = ReporterUserFactory(
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        reporter.party = party
        reporter.save()
        submission = SubmissionFactory(
            party=party,
            created_by=reporter,
            last_edited_by=reporter,
        )
        submission._current_state = 'submitted'
        submission.save()

        reporter_same_party = ReporterUserFactory(
            party=party,
            username='reporter_same_party',
            email='reporter_same_party@example.com',
            password=self.hash_alg.encode(password='qwe123qwe',
                                          salt='123salt123')
        )
        headers = self.get_authorization_header(reporter_same_party.username, 'qwe123qwe')
        resp = self.client.post(
            reverse("core:submission-clone",
                    kwargs={'pk': submission.pk}),
            {"party": party.pk},
            **headers
        )
        self.assertEqual(resp.status_code, 200)

    def test_clone_another_party(self):
        """
        Testing `clone` action using a party reporter user for a submission
        created by another user from another party.
        Expected result: 403 Forbidden.
        """

        party = PartyFactory(subregion=self.subregion)
        reporter = ReporterUserFactory(
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        reporter.party = party
        reporter.save()
        submission = SubmissionFactory(
            party=party,
            created_by=reporter,
            last_edited_by=reporter,
        )
        submission._current_state = 'submitted'
        submission.save()

        another_party = PartyFactory(
            abbr='AP',
            name='Another Party',
            subregion=self.subregion
        )
        reporter_another_party = ReporterUserFactory(
            party=another_party,
            username='reporter_another_party',
            email='reporter_another_party@example.com',
            password=self.hash_alg.encode(password='qwe123qwe',
                                          salt='123salt123')
        )
        headers = self.get_authorization_header(reporter_another_party.username, 'qwe123qwe')
        resp = self.client.post(
            reverse("core:submission-clone",
                    kwargs={'pk': submission.pk}),
            {"party": party.pk},
            **headers
        )
        self.assertEqual(resp.status_code, 403)
