from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import Argon2PasswordHasher

from .base import BaseTests
from .factories import (
    PartyFactory,
    ReporterUserFactory,
    SubregionFactory,
    RegionFactory,
    ReportingChannelFactory,
    LanguageEnFactory,
    LanguageFrFactory
)

User = get_user_model()


REPORTER_ACCOUNT_DATA = {
    'email': 'reporter@example.com',
    'first_name': 'Test',
    'last_name': 'Test',
    'role': 'Party Reporter',
    'is_secretariat': False,
    'is_read_only': False
}


class UserAccountTests(BaseTests):

    def setUp(self):
        super().setUp()
        hash_alg = Argon2PasswordHasher()
        region = RegionFactory.create()
        subregion = SubregionFactory.create(region=region)
        party = PartyFactory.create(subregion=subregion)
        self.language_en = LanguageEnFactory()
        self.language_fr= LanguageFrFactory()
        self.reporter = ReporterUserFactory.create(
            first_name='Test',
            last_name='Test',
            email='reporter@example.com',
            language=self.language_en,
            party=party,
            password=hash_alg.encode(password='qwe123qwe', salt='123salt123'),
        )
        self.client.login(username=self.reporter.username, password='qwe123qwe')
        ReportingChannelFactory()

    def test_get_user_account(self):
        result = self.client.get(
            reverse(
                "core:current_user-detail",
                kwargs={"pk": self.reporter.pk}
            )
        )
        self.assertEqual(result.status_code, 200)
        expected_data = dict(REPORTER_ACCOUNT_DATA)
        expected_data['id'] = self.reporter.pk
        expected_data['username'] = self.reporter.username
        expected_data['party'] = self.reporter.party.pk
        expected_data['language'] = self.reporter.language.pk
        self.assertEqual(result.json(), expected_data)

    def test_update_user_account(self):
        data = dict(REPORTER_ACCOUNT_DATA)
        data['email'] = 'reporter_edited@example.com'
        data['first_name'] = 'Test Edited'
        data['last_name'] = 'Test Edited'
        data['language'] = self.language_fr.pk

        result = self.client.put(
            reverse(
                "core:current_user-detail",
                kwargs={"pk": self.reporter.pk}
            ),
            data
        )
        self.assertEqual(result.status_code, 200)
        user = User.objects.get(pk=self.reporter.pk)
        self.assertEqual(user.email, 'reporter_edited@example.com')
        self.assertEqual(user.first_name, 'Test Edited')
        self.assertEqual(user.last_name, 'Test Edited')
        self.assertEqual(user.language, self.language_fr)
