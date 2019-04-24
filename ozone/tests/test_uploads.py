import io
import os
import time
import socket
import unittest

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.core.servers.basehttp import ThreadedWSGIServer, WSGIRequestHandler
from django.test.testcases import LiveServerThread
from tusclient import client

from django.urls import reverse
from django.test import LiveServerTestCase
from django.contrib.auth.hashers import Argon2PasswordHasher

from .base import BaseTests
from .factories import (
    PartyFactory,
    RegionFactory,
    ReportingPeriodFactory,
    ObligationFactory,
    LanguageEnFactory,
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
        ContentType.objects.clear_cache()
        self.workflow_class = "default"

        self.region = RegionFactory.create()
        self.period = ReportingPeriodFactory.create(name="Some period")
        self.obligation = ObligationFactory.create(name="Some obligation")
        self.subregion = SubregionFactory.create(region=self.region)
        self.party = PartyFactory(subregion=self.subregion)
        self.another_party = AnotherPartyFactory(subregion=self.subregion)
        self.language = LanguageEnFactory()

        hash_alg = Argon2PasswordHasher()
        self.secretariat_user = SecretariatUserFactory(
            language=self.language,
            password=hash_alg.encode(password="qwe123qwe", salt="123salt123")
        )
        self.party_user = ReporterUserFactory(
            language=self.language,
            party=self.party,
            password=hash_alg.encode(password="qwe123qwe", salt="123salt123"),
        )
        self.another_party_user = ReporterUserAnotherPartyFactory(
            language=self.language,
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


class TestToken(BaseSubmissionTest, BaseTests):
    def test_create_token_as_party(self):
        submission = self.create_submission()
        self.client.login(username=self.party_user.username, password='qwe123qwe')
        resp = self.client.post(
            reverse(
                "core:submission-token-list", kwargs={"submission_pk": submission.pk}
            ),
        )
        # Party cannot create token on secretariat submission
        self.assertEqual(resp.status_code, 403)

    def test_create_token_as_party_wrong_party(self):
        submission = self.create_submission()
        self.client.login(
            username=self.another_party_user.username, password='qwe123qwe'
        )
        resp = self.client.post(
            reverse(
                "core:submission-token-list",
                kwargs={"submission_pk": submission.pk}
            ),
        )
        self.assertEqual(resp.status_code, 403)

    def test_create_token_as_secretariat(self):
        submission = self.create_submission()
        self.client.login(
            username=self.secretariat_user.username, password='qwe123qwe'
        )
        resp = self.client.post(
            reverse(
                "core:submission-token-list",
                kwargs={"submission_pk": submission.pk}
            ),
        )
        self.assertEqual(resp.status_code, 200)


class ReuseLiveServerThread(LiveServerThread):
    """
    Enables SO_REUSEADDR, avoid errors while the socket is still in TIME_WAIT.
    """

    def _create_server(self):
        return ThreadedWSGIServer(
            (self.host, self.port),
            WSGIRequestHandler,
            allow_reuse_address=True
        )


@unittest.skipIf(not TUSD_AVAILABLE, "TUSD not available!")
class TestUpload(BaseSubmissionTest, LiveServerTestCase):
    port = 8000
    tus_host = f"http://{settings.TUSD_HOST}:{settings.TUSD_PORT}/files/"
    server_thread_class = ReuseLiveServerThread

    def tearDown(self):
        super().tearDown()
        ContentType.objects.clear_cache()
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
                "description": "description",
                "token": token.token,
            }
        )
        uploader.upload()
        self.assertTrue(uploader.verify_upload())
        # XXX Wait to (hopefully) ensure that tusd has finished
        time.sleep(2)
        self.assertEqual(submission.files.first().name, "text.txt")
        self.assertEqual(submission.files.first().description, "description")
        self.assertEqual(submission.files.first().file.read(), FILE_CONTENT)

    def test_upload_as_secretariat(self):
        submission, token = self.create_submission(self.secretariat_user)
        tus = client.TusClient(self.tus_host)
        stream = io.BytesIO(FILE_CONTENT)
        uploader = tus.uploader(
            file_stream=stream, chunk_size=200,
            metadata={
                "filename": "text.txt",
                "description": "description",
                "token": token.token,
            }
        )
        uploader.upload()
        self.assertTrue(uploader.verify_upload())
        # XXX Wait to (hopefully) ensure that tusd has finished
        time.sleep(2)
        self.assertEqual(submission.files.first().name, "text.txt")
        self.assertEqual(submission.files.first().description, "description")
        self.assertEqual(submission.files.first().file.read(), FILE_CONTENT)

# TODO: test edge cases: expired token, invalid token, wrong extension,
# TODO: token cleanup at the end.


class TestListFiles(BaseSubmissionTest, BaseTests):

    def test_list_files_as_party(self):
        submission = self.create_submission()
        submission_file = self.create_file(submission)

        self.client.login(username=self.party_user.username, password='qwe123qwe')
        resp = self.client.get(
            reverse(
                "core:submission-files-list",
                kwargs={"submission_pk": submission.pk}
            ),
        )
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(resp.json()[0]['name'], submission_file.name)

    def test_list_files_as_secretariat(self):
        submission = self.create_submission()
        submission_file = self.create_file(submission)

        self.client.login(
            username=self.secretariat_user.username, password='qwe123qwe'
        )
        resp = self.client.get(
            reverse(
                "core:submission-files-list",
                kwargs={"submission_pk": submission.pk}
            ),
        )
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(resp.json()[0]['name'], submission_file.name)


class TestChangeDetails(BaseSubmissionTest, BaseTests):
    """
    Only name and description can be changed through the API.
    """
    def test_change_files_as_party(self):
        submission = self.create_submission()
        self.create_file(submission)

        self.client.login(
            username=self.party_user.username, password='qwe123qwe'
        )

        files_list_url = reverse(
            "core:submission-files-list",
            kwargs={"submission_pk": submission.pk}
        )

        resp = self.client.get(files_list_url)

        json_response = resp.json()
        json_response[0]['name'] = 'text_modified.txt'
        json_response[0]['description'] = 'description modified'

        self.client.put(files_list_url, json_response)

        self.assertEqual(resp.json()[0]['name'], 'text_modified.txt')
        self.assertEqual(
            resp.json()[0]['description'], 'description modified'
        )

    def test_change_files_as_secretariat(self):
        submission = self.create_submission()
        self.create_file(submission)

        self.client.login(
            username=self.secretariat_user.username, password='qwe123qwe'
        )

        files_list_url = reverse(
            "core:submission-files-list",
            kwargs={"submission_pk": submission.pk}
        )
        resp = self.client.get(files_list_url)
        json_response = resp.json()
        json_response[0]['name'] = 'text_modified.txt'
        json_response[0]['description'] = 'description modified'

        self.client.put(files_list_url, json_response)
        self.assertEqual(resp.json()[0]['name'], 'text_modified.txt')
        self.assertEqual(
            resp.json()[0]['description'], 'description modified'
        )


class TestDownloads(BaseSubmissionTest, BaseTests):

    def test_download_files_as_party(self):
        submission = self.create_submission()
        submission_file = self.create_file(submission)

        self.client.login(
            username=self.party_user.username, password='qwe123qwe'
        )
        resp = self.client.get(
            reverse(
                "core:submission-files-download",
                kwargs={
                    "submission_pk": submission.pk,
                    "pk": submission_file.pk
                }
            ),
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, submission_file.file.read())

    def test_download_files_as_different_party(self):
        submission = self.create_submission()
        submission_file = self.create_file(submission)

        self.client.login(
            username=self.another_party_user.username, password='qwe123qwe'
        )
        resp = self.client.get(
            reverse(
                "core:submission-files-download",
                kwargs={
                    "submission_pk": submission.pk, "pk": submission_file.pk
                }
            ),
        )
        self.assertEqual(resp.status_code, 403)

    def test_download_files_as_secretariat(self):
        submission = self.create_submission()
        submission_file = self.create_file(submission)

        self.client.login(
            username=self.secretariat_user.username, password='qwe123qwe'
        )
        resp = self.client.get(
            reverse(
                "core:submission-files-download",
                kwargs={
                    "submission_pk": submission.pk, "pk": submission_file.pk
                }
            ),
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, submission_file.file.read())

    def test_download_files_nonascii(self):
        submission = self.create_submission()
        submission_file = self.create_file(submission, 'العربية')

        self.client.login(
            username=self.secretariat_user.username, password='qwe123qwe'
        )
        resp = self.client.get(
            reverse(
                "core:submission-files-download",
                kwargs={
                    "submission_pk": submission.pk, "pk": submission_file.pk
                }
            ),
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, submission_file.file.read())
