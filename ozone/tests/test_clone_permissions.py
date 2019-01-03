from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import Argon2PasswordHasher

from .factories import (
    AnotherPartyFactory,
    PartyFactory,
    RegionFactory,
    ReporterUserFactory,
    ReporterUserSamePartyFactory,
    ReporterUserAnotherPartyFactory,
    ReportingChannelFactory,
    SecretariatUserFactory,
    SubmissionFactory,
    SubregionFactory,
)


User = get_user_model()


class ClonePermissionsTests(TestCase):

    def setUp(self):
        super().setUp()

        self.region = RegionFactory.create()
        self.subregion = SubregionFactory.create(region=self.region)
        self.party = PartyFactory(subregion=self.subregion)
        self.another_party = AnotherPartyFactory(subregion=self.subregion)

        hash_alg = Argon2PasswordHasher()
        self.secretariat_user = SecretariatUserFactory(
            password=hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        self.reporter = ReporterUserFactory(
            party=self.party,
            password=hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        self.reporter_same_party = ReporterUserSamePartyFactory(
            party=self.party,
            password=hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        self.reporter_another_party = ReporterUserAnotherPartyFactory(
            party=self.another_party,
            password=hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        ReportingChannelFactory()


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

        submission = SubmissionFactory(
            party=self.party,
            created_by=self.secretariat_user,
            last_edited_by=self.secretariat_user,
        )
        submission._current_state = 'submitted'
        submission.save()
        headers = self.get_authorization_header(self.secretariat_user.username, 'qwe123qwe')
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

        submission = SubmissionFactory(
            party=self.party,
            created_by=self.reporter,
            last_edited_by=self.reporter,
        )
        submission._current_state = 'submitted'
        submission.save()

        headers = self.get_authorization_header(self.reporter_same_party.username, 'qwe123qwe')
        resp = self.client.post(
            reverse("core:submission-clone",
                    kwargs={'pk': submission.pk}),
            {"party": self.party.pk},
            **headers
        )
        self.assertEqual(resp.status_code, 200)

    def test_clone_another_party(self):
        """
        Testing `clone` action using a party reporter user for a submission
        created by another user from another party.
        Expected result: 403 Forbidden.
        """

        submission = SubmissionFactory(
            party=self.party,
            created_by=self.reporter,
            last_edited_by=self.reporter,
        )
        submission._current_state = 'submitted'
        submission.save()

        headers = self.get_authorization_header(self.reporter_another_party.username, 'qwe123qwe')
        resp = self.client.post(
            reverse("core:submission-clone",
                    kwargs={'pk': submission.pk}),
            {"party": self.party.pk},
            **headers
        )
        self.assertEqual(resp.status_code, 403)

    def test_clone_secretariat_another_party(self):
        """
        Testing `clone` action using a party reporter user for a submission from
        a different party, created by a secretariat user.
        Expected result: 403 Forbidden.
        """

        submission = SubmissionFactory(
            party=self.another_party,
            created_by=self.secretariat_user,
            last_edited_by=self.secretariat_user,
        )
        submission._current_state = 'submitted'
        submission.save()

        headers = self.get_authorization_header(self.reporter.username, 'qwe123qwe')
        resp = self.client.post(
            reverse("core:submission-clone",
                    kwargs={'pk': submission.pk}),
            {"party": self.party.pk},
            **headers
        )
        self.assertEqual(resp.status_code, 403)
