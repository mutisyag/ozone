from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient


class BaseTests(TestCase):
    """
    Use APIClient instead of Django default Client to help us authenticate the
    user easily. Also we can pass the data to HTTP call as a Python dictionary,
    without the need to convert it into json.
    """
    client_class = APIClient
