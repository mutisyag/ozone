import json
import unittest

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import Argon2PasswordHasher

from ozone.core.models import HighAmbientTemperatureImport, Submission

from .factories import (
    PartyFactory,
    RegionFactory,
    ReporterUserFactory,
    ReportingChannelFactory,
    SecretariatUserFactory,
    SubmissionFactory,
    SubregionFactory,
    SubstanceFactory,
    AnotherPartyFactory,
    HighAmbientTemperatureImportFactory,
)


class BaseHATImportTest(TestCase):
    def setUp(self):
        super().setUp()
        self.workflow_class = "default"

        self.region = RegionFactory.create()
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
        submission = SubmissionFactory(
            party=self.party, created_by=self.secretariat_user,
            last_edited_by=self.secretariat_user, **kwargs
        )
        return submission


HAT_IMPORT_DATA = {
    'quantity_msac': 100,
    'quantity_sdac': 101,
    'quantity_dcpac': 102,
    'remarks_os': 'nothing to remark OS',
    'remarks_party': 'nothing to remark'
}


class TestHATImport(BaseHATImportTest):

    def test_create(self):
        submission = self.create_submission()

        headers = self.get_authorization_header(self.secretariat_user.username, "qwe123qwe")

        data = dict(HAT_IMPORT_DATA)
        data["substance"] = self.substance.id

        result = self.client.post(
            reverse(
                "core:submission-hat-imports-list",
                kwargs={"submission_pk": submission.pk},
            ),
            json.dumps([data]),
            "application/json",
            format="json",
            **headers,
        )
        self.assertEqual(result.status_code, 201, result.json())

    def test_get(self):
        submission = self.create_submission()

        hat_import = HighAmbientTemperatureImportFactory(
            submission=submission, substance=self.substance,
            **HAT_IMPORT_DATA
        )

        headers = self.get_authorization_header(self.secretariat_user.username, "qwe123qwe")

        result = self.client.get(
            reverse(
                "core:submission-hat-imports-list",
                kwargs={"submission_pk": submission.pk},
            ),
            format="json",
            **headers,
        )
        self.assertEqual(result.status_code, 200, result.json())

        expected_data = dict(HAT_IMPORT_DATA)
        expected_data["substance"] = self.substance.id
        expected_data["blend"] = None
        expected_data["derived_substance_data"] = []
        expected_data["id"] = hat_import.id
        expected_data["ordering_id"] = 0
        expected_data["group"] = ''

        self.assertEqual(result.json(), [expected_data])

    def test_update(self):
        submission = self.create_submission()

        hat_import = HighAmbientTemperatureImportFactory(
            submission=submission, substance=self.substance,
            **HAT_IMPORT_DATA
        )

        data = dict(HAT_IMPORT_DATA)
        data["substance"] = self.substance.id
        data["quantity_msac"] = 42

        headers = self.get_authorization_header(self.secretariat_user.username, "qwe123qwe")

        result = self.client.put(
            reverse(
                "core:submission-hat-imports-list",
                kwargs={"submission_pk": submission.pk},
            ),
            json.dumps([data]),
            "application/json",
            format="json",
            **headers,
        )
        self.assertEqual(result.status_code, 200, result.json())

        hat_import = HighAmbientTemperatureImport.objects.get(pk=hat_import.id)
        self.assertEqual(hat_import.quantity_msac, 42)

    def test_update_immutable(self):
        submission = self.create_submission()

        hat_import = HighAmbientTemperatureImportFactory(
            submission=submission, substance=self.substance,
            **HAT_IMPORT_DATA
        )
        submission._current_state = "finalized"
        submission.save()

        data = dict(HAT_IMPORT_DATA)
        data["substance"] = self.substance.id
        data["quantity_msac"] = 42

        headers = self.get_authorization_header(self.secretariat_user.username, "qwe123qwe")

        result = self.client.put(
            reverse(
                "core:submission-hat-imports-list",
                kwargs={"submission_pk": submission.pk},
            ),
            json.dumps([data]),
            "application/json",
            format="json",
            **headers,
        )
        self.assertEqual(result.status_code, 422, result.json())

    def test_clone(self):
        submission = self.create_submission()

        hat_import = HighAmbientTemperatureImportFactory(
            submission=submission, substance=self.substance,
            **HAT_IMPORT_DATA
        )
        submission._current_state = "finalized"
        submission.save()

        headers = self.get_authorization_header(self.secretariat_user.username, "qwe123qwe")

        result = self.client.post(
            reverse(
                "core:submission-clone",
                kwargs={"pk": submission.pk},
            ),
            format="json",
            **headers,
        )
        self.assertEqual(result.status_code, 200, result.json())
        new_id = result.json()['url'].split("/")[-2]

        new_hat = Submission.objects.get(pk=new_id).highambienttemperatureimports.first()
        self.assertEqual({
            'quantity_msac': new_hat.quantity_msac,
            'quantity_sdac': new_hat.quantity_sdac,
            'quantity_dcpac': new_hat.quantity_dcpac,
            'remarks_os': new_hat.remarks_os,
            'remarks_party': new_hat.remarks_party,
        }, HAT_IMPORT_DATA)