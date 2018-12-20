from django.urls import reverse
from django.contrib.auth import get_user_model

from .base import BaseTests

User = get_user_model()


class EmailAuthTests(BaseTests):

    def setUp(self):
        self.user = User.objects.create_user(
            username="user1",
            email='test@example.com',
            password='qwe123qwe'
        )

    def test_login(self):
        login = self.client.login(username=self.user.username, password='qwe123qwe')
        self.assertTrue(login)

    def test_get_token(self):
        resp = self.client.post(reverse("core:auth-token-list"), {
            "username": self.user.username,
            "password": "qwe123qwe"
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn('token', resp.data)
