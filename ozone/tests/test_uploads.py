import io
import os
import time
import socket
import unittest

from django.conf import settings
from django.core.servers.basehttp import ThreadedWSGIServer, WSGIRequestHandler
from django.test.testcases import LiveServerThread
from tusclient import client

from django.urls import reverse
from django.test import LiveServerTestCase
from django.contrib.auth.hashers import Argon2PasswordHasher

from ozone.core.models import Submission, SubmissionInfo

from .base import BaseTests
from .factories import (
    PartyFactory,
    RegionFactory,
    ReportingPeriodFactory,
    ObligationFactory,
    ReporterUserFactory,
    ReporterUserAnotherPartyFactory,
    ReportingChannelFactory,
    SecretariatUserFactory,
    SubmissionFactory,
    SubregionFactory,
    SubstanceFactory,
    AnotherPartyFactory,
    UploadTokenFactory,
)


FILE_CONTENT = b"X" * 100
TUSD_AVAILABLE = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM
).connect_ex(
    (settings.TUSD_HOST, int(settings.TUSD_PORT))
) == 0



class BaseSubmissionTest(object):
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
        self.party_user = ReporterUserFactory(
            party=self.party,
            password=hash_alg.encode(password="qwe123qwe", salt="123salt123"),
        )
        self.another_party_user = ReporterUserAnotherPartyFactory(
            party=self.another_party,
            password=hash_alg.encode(password="qwe123qwe", salt="123salt123"),
        )
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


class TestToken(BaseSubmissionTest, BaseTests):
    def test_create_token_as_party(self):
        submission = self.create_submission()
        self.client.login(username=self.party_user.username, password='qwe123qwe')
        resp = self.client.post(
            reverse(
                "core:submission-token-list", kwargs={"submission_pk": submission.pk}
            ),
        )
        self.assertEqual(resp.status_code, 200)

    def test_create_token_as_party_wrong_party(self):
        submission = self.create_submission()
        self.client.login(username=self.another_party_user.username, password='qwe123qwe')
        resp = self.client.post(
            reverse(
                "core:submission-token-list", kwargs={"submission_pk": submission.pk}
            ),
        )
        self.assertEqual(resp.status_code, 403)

    def test_create_token_as_secretariat(self):
        submission = self.create_submission()
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.client.post(
            reverse(
                "core:submission-token-list", kwargs={"submission_pk": submission.pk}
            ),
        )
        self.assertEqual(resp.status_code, 200)


class ReuseLiveServerThread(LiveServerThread):
    """Enables SO_REUSEADDR, avoid errors while the socket is still in TIME_WAIT."""

    def _create_server(self):
        return ThreadedWSGIServer((self.host, self.port), WSGIRequestHandler, allow_reuse_address=True)


@unittest.skipIf(not TUSD_AVAILABLE, "TUSD not available!")
class TestUpload(BaseSubmissionTest, LiveServerTestCase):
    port = 8000
    tus_host = f"http://{settings.TUSD_HOST}:{settings.TUSD_PORT}/files/"
    server_thread_class = ReuseLiveServerThread

    def tearDown(self):
        super().tearDown()
        for filename in os.listdir(settings.TUSD_UPLOADS_DIR):
            try:
                os.remove(os.path.join(settings.TUSD_UPLOADS_DIR, filename))
            except OSError:
                pass

    def create_submission(self, user, **kwargs):
        submission = super().create_submission(**kwargs)
        token = UploadTokenFactory.create(submission=submission, user=user)
        return submission, token

    def test_upload_as_party(self):
        submission, token = self.create_submission(self.party_user)
        tus = client.TusClient(self.tus_host)
        stream = io.BytesIO(FILE_CONTENT)
        uploader = tus.uploader(
            file_stream=stream, chunk_size=200,
            metadata={
                "filename": "text.txt",
                "token": token.token,
            }
        )
        uploader.upload()
        self.assertTrue(uploader.verify_upload())
        # XXX Wait to (hopefully) ensure that tusd has finished
        time.sleep(2)
        self.assertEqual(submission.files.first().name, "text.txt")
        self.assertEqual(submission.files.first().file.read(), FILE_CONTENT)

    def test_upload_as_secretariat(self):
        submission, token = self.create_submission(self.secretariat_user)
        tus = client.TusClient(self.tus_host)
        stream = io.BytesIO(FILE_CONTENT)
        uploader = tus.uploader(
            file_stream=stream, chunk_size=200,
            metadata={
                "filename": "text.txt",
                "token": token.token,
            }
        )
        uploader.upload()
        self.assertTrue(uploader.verify_upload())
        # XXX Wait to (hopefully) ensure that tusd has finished
        time.sleep(2)
        self.assertEqual(submission.files.first().name, "text.txt")
        self.assertEqual(submission.files.first().file.read(), FILE_CONTENT)

# TODO: test edge cases: expired token, invalid token, wrong extension,
# TODO: token cleanup at the end.
