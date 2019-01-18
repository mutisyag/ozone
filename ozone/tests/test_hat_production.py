import json
import unittest

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import Argon2PasswordHasher

from ozone.core.models import HighAmbientTemperatureProduction, Submission

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
    HighAmbientTemperatureProductionFactory,
    ObligationFactory,
)


class BaseHATProductionTest(TestCase):
    def setUp(self):
        super().setUp()
        self.workflow_class = "default"

        self.obligation = ObligationFactory(form_type="hat")
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
            obligation=self.obligation, party=self.party, created_by=self.secretariat_user,
            last_edited_by=self.secretariat_user, **kwargs
        )
        return submission


HAT_PROD_DATA = {
    'quantity_msac': 100,
    'quantity_sdac': 101,
    'quantity_dcpac': 102,
    'remarks_os': 'nothing to remark OS',
    'remarks_party': 'nothing to remark'
}


class TestHATProduction(BaseHATProductionTest):

    def test_create(self):
        submission = self.create_submission()

        headers = self.get_authorization_header(self.secretariat_user.username, "qwe123qwe")

        data = dict(HAT_PROD_DATA)
        data["substance"] = self.substance.id

        result = self.client.post(
            reverse(
                "core:submission-hat-productions-list",
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

        hat_prod = HighAmbientTemperatureProductionFactory(
            submission=submission, substance=self.substance,
            **HAT_PROD_DATA
        )

        headers = self.get_authorization_header(self.secretariat_user.username, "qwe123qwe")

        result = self.client.get(
            reverse(
                "core:submission-hat-productions-list",
                kwargs={"submission_pk": submission.pk},
            ),
            format="json",
            **headers,
        )
        self.assertEqual(result.status_code, 200, result.json())

        expected_data = dict(HAT_PROD_DATA)
        expected_data["substance"] = self.substance.id
        expected_data["id"] = hat_prod.id
        expected_data["ordering_id"] = 0
        expected_data["group"] = ''

        self.assertEqual(result.json(), [expected_data])

    def test_update(self):
        submission = self.create_submission()

        hat_prod = HighAmbientTemperatureProductionFactory(
            submission=submission, substance=self.substance,
            **HAT_PROD_DATA
        )

        data = dict(HAT_PROD_DATA)
        data["substance"] = self.substance.id
        data["quantity_msac"] = 42

        headers = self.get_authorization_header(self.secretariat_user.username, "qwe123qwe")

        result = self.client.put(
            reverse(
                "core:submission-hat-productions-list",
                kwargs={"submission_pk": submission.pk},
            ),
            json.dumps([data]),
            "application/json",
            format="json",
            **headers,
        )
        self.assertEqual(result.status_code, 200, result.json())

        hat_prod = HighAmbientTemperatureProduction.objects.get(pk=hat_prod.id)
        self.assertEqual(hat_prod.quantity_msac, 42)

    def test_update_immutable(self):
        submission = self.create_submission()
        hat_prod = HighAmbientTemperatureProductionFactory(
            submission=submission, substance=self.substance,
            **HAT_PROD_DATA
        )
        submission._current_state = "finalized"
        submission.save()

        data = dict(HAT_PROD_DATA)
        data["substance"] = self.substance.id
        data["quantity_msac"] = 42

        headers = self.get_authorization_header(self.secretariat_user.username, "qwe123qwe")

        result = self.client.put(
            reverse(
                "core:submission-hat-productions-list",
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

        hat_prod = HighAmbientTemperatureProductionFactory(
            submission=submission, substance=self.substance,
            **HAT_PROD_DATA
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

        new_hat = Submission.objects.get(pk=new_id).highambienttemperatureproductions.first()
        self.assertEqual({
            'quantity_msac': new_hat.quantity_msac,
            'quantity_sdac': new_hat.quantity_sdac,
            'quantity_dcpac': new_hat.quantity_dcpac,
            'remarks_os': new_hat.remarks_os,
            'remarks_party': new_hat.remarks_party,
        }, HAT_PROD_DATA)
