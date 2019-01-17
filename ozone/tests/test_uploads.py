import io
import os
import time
import socket
import unittest

from django.conf import settings
from django.core.files import File
from django.core.servers.basehttp import ThreadedWSGIServer, WSGIRequestHandler
from django.test.testcases import LiveServerThread
from tusclient import client

from django.urls import reverse
from django.test import TestCase, LiveServerTestCase
from django.contrib.auth.hashers import Argon2PasswordHasher

from ozone.core.models import Submission, SubmissionInfo

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
    SubmissionFileFactory,
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

    def get_authorization_header(self, username, password):
        resp = self.client.post(
            reverse("core:auth-token-list"),
            {"username": username, "password": password},
            format="json",
        )
        return {"HTTP_AUTHORIZATION": "Token " + resp.data["token"]}

    def create_submission(self, **kwargs):
        submission = SubmissionFactory.create(
            party=self.party,
            created_by=self.secretariat_user,
            last_edited_by=self.secretariat_user,
            **kwargs,
        )
        return submission

    def create_file(self, submission, filename='test_file.txt'):
        submission_file = SubmissionFileFactory.create(
            submission=submission,
            name=filename,
            uploader=self.secretariat_user,
            tus_id=None,
            upload_successful=True
        )
        stream = io.BytesIO(FILE_CONTENT)
        submission_file.file.save(filename, File(stream))
        return submission_file


class TestToken(BaseSubmissionTest, TestCase):
    def test_create_token_as_party(self):
        submission = self.create_submission()
        headers = self.get_authorization_header(self.party_user.username, "qwe123qwe")
        resp = self.client.post(
            reverse(
                "core:submission-token-list", kwargs={"submission_pk": submission.pk}
            ),
            **headers,
        )
        self.assertEqual(resp.status_code, 200)

    def test_create_token_as_party_wrong_party(self):
        submission = self.create_submission()
        headers = self.get_authorization_header(
            self.another_party_user.username, "qwe123qwe"
        )
        resp = self.client.post(
            reverse(
                "core:submission-token-list", kwargs={"submission_pk": submission.pk}
            ),
            **headers,
        )
        self.assertEqual(resp.status_code, 403)

    def test_create_token_as_secretariat(self):
        submission = self.create_submission()
        headers = self.get_authorization_header(
            self.secretariat_user.username, "qwe123qwe"
        )
        resp = self.client.post(
            reverse(
                "core:submission-token-list", kwargs={"submission_pk": submission.pk}
            ),
            **headers,
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


class TestListFiles(BaseSubmissionTest, TestCase):

    def test_list_files_as_party(self):
        submission = self.create_submission()
        submission_file = self.create_file(submission)

        headers = self.get_authorization_header(self.party_user, "qwe123qwe")
        resp = self.client.get(
            reverse(
                "core:submission-files-list",
                kwargs={"submission_pk": submission.pk}
            ),
            **headers
        )
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(resp.json()[0]['name'], submission_file.name)

    def test_list_files_as_secretariat(self):
        submission = self.create_submission()
        submission_file = self.create_file(submission)

        headers = self.get_authorization_header(self.party_user, "qwe123qwe")
        resp = self.client.get(
            reverse(
                "core:submission-files-list",
                kwargs={"submission_pk": submission.pk}
            ),
            **headers
        )
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(resp.json()[0]['name'], submission_file.name)


class TestDownloads(BaseSubmissionTest, TestCase):

    def test_download_files_as_party(self):
        submission = self.create_submission()
        submission_file = self.create_file(submission)

        headers = self.get_authorization_header(self.party_user, "qwe123qwe")
        resp = self.client.get(
            reverse(
                "core:submission-files-download",
                kwargs={"submission_pk": submission.pk, "pk": submission_file.pk}
            ),
            **headers
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, submission_file.file.read())

    def test_download_files_as_different_party(self):
        submission = self.create_submission()
        submission_file = self.create_file(submission)

        headers = self.get_authorization_header(self.another_party_user, "qwe123qwe")
        resp = self.client.get(
            reverse(
                "core:submission-files-download",
                kwargs={"submission_pk": submission.pk, "pk": submission_file.pk}
            ),
            **headers
        )
        self.assertEqual(resp.status_code, 403)

    def test_download_files_as_secretariat(self):
        submission = self.create_submission()
        submission_file = self.create_file(submission)

        headers = self.get_authorization_header(self.secretariat_user, "qwe123qwe")
        resp = self.client.get(
            reverse(
                "core:submission-files-download",
                kwargs={"submission_pk": submission.pk, "pk": submission_file.pk}
            ),
            **headers
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, submission_file.file.read())

    def test_download_files_nonascii(self):
        submission = self.create_submission()
        submission_file = self.create_file(submission, 'العربية')

        headers = self.get_authorization_header(self.secretariat_user, "qwe123qwe")
        resp = self.client.get(
            reverse(
                "core:submission-files-download",
                kwargs={"submission_pk": submission.pk, "pk": submission_file.pk}
            ),
            **headers
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, submission_file.file.read())
