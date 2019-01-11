from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient


class BaseTests(TestCase):
    client_class = APIClient

    def get_token(self, username, password):
        resp = self.client.post(reverse("core:auth-token-list"), {
            "username": username,
            "password": password,
        })
        return resp.data['token']
