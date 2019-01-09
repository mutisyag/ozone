import json

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import Argon2PasswordHasher

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
    DestructionFactory,
    ProductionFactory,
    ImportFactory,
    ExportFactory,
    EmissionFactory,
    NonPartyTradeFactory,
    HighAmbientTemperatureImportFactory,
    HighAmbientTemperatureProductionFactory,
)

User = get_user_model()


class BaseDataRemarksTestsMixIn(object):
    """Base class for the data remarks permissions tests.

    Creates basic objects in the setUp, and implements all possible
    tests cases.

    The actual `check_remark` is not implemented.
    """

    api = None
    api_data = {}

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

    def create_submission(self, owner, **kwargs):
        submission = SubmissionFactory(
            party=self.party, created_by=owner, last_edited_by=owner, **kwargs
        )
        return submission

    def _check_result(self, result, expect_success):
        try:
            verbose = result.json()
        except:
            verbose = result.data
        self.assertEqual(
            result.status_code,
            self.success_code if expect_success else self.fail_code,
            verbose,
        )

    def check_remark(self, user, field, owner, expect_success):
        raise NotImplementedError()

    def test_party_user_party_field_party_reporter(self):
        self.check_remark(self.party_user, "party", self.party_user, True)

    def test_party_user_party_filed_secretariat_reporter(self):
        self.check_remark(self.party_user, "party", self.secretariat_user, True)

    def test_party_user_secretariat_field_party_reporter(self):
        self.check_remark(self.party_user, "os", self.party_user, False)

    def test_party_user_secretariat_field_secretariat_reporter(self):
        self.check_remark(self.party_user, "os", self.secretariat_user, False)

    def test_secretariat_user_party_field_party_reporter(self):
        self.check_remark(self.secretariat_user, "party", self.party_user, False)

    def test_secretariat_user_party_field_secretariat_reporter(self):
        self.check_remark(self.secretariat_user, "party", self.secretariat_user, True)

    def test_secretariat_user_secretariat_field_party_reporter(self):
        self.check_remark(self.secretariat_user, "os", self.party_user, True)

    def test_secretariat_user_secretariat_field_secretariat_reporter(self):
        self.check_remark(self.secretariat_user, "os", self.secretariat_user, True)


class BaseDataCreateRemarksTestsMixIn(BaseDataRemarksTestsMixIn):
    """Checks the remark permissions when a new data entry is added."""

    no_substance = False
    success_code = 201
    fail_code = 422

    def check_remark(self, user, field, owner, expect_success):
        field = "remarks_%s" % field

        submission = self.create_submission(owner)
        headers = self.get_authorization_header(user.username, "qwe123qwe")

        data = dict(self.api_data)
        if not self.no_substance:
            data["substance"] = self.substance.id
        data[field] = "Some random remark here."

        result = self.client.post(
            reverse(self.api, kwargs={"submission_pk": submission.pk}),
            data,
            "application/json",
            format="json",
            **headers,
        )

        self._check_result(result, expect_success)


class BaseDataUpdateRemarksTestsMixIn(BaseDataRemarksTestsMixIn):
    """Checks the remark permissions when a data entry is updated."""

    success_code = 200
    fail_code = 422
    no_substance = False
    factory_klass = None

    def check_remark(self, user, field, owner, expect_success):
        field = "remarks_%s" % field

        submission = self.create_submission(owner)

        args = dict(self.api_data)
        args["submission"] = submission
        if not self.no_substance:
            args["substance"] = self.substance

        data_entry = self.factory_klass(**args)

        data = dict(self.api_data)
        if not self.no_substance:
            data["substance"] = self.substance.id
        data[field] = "Some random remark here."

        headers = self.get_authorization_header(user.username, "qwe123qwe")

        result = self.client.put(
            reverse(self.api, kwargs={"submission_pk": submission.id}),
            json.dumps([data]),
            "application/json",
            format="json",
            **headers,
        )
        self._check_result(result, expect_success)


class ImportDataCheckCreate(BaseDataCreateRemarksTestsMixIn, TestCase):
    api = "core:submission-article7-imports-list"


class ImportDataCheckUpdate(BaseDataUpdateRemarksTestsMixIn, TestCase):
    api = "core:submission-article7-imports-list"
    factory_klass = ImportFactory


class ExportDataCheckCreate(BaseDataCreateRemarksTestsMixIn, TestCase):
    api = "core:submission-article7-exports-list"


class ExportDataCheckUpdate(BaseDataUpdateRemarksTestsMixIn, TestCase):
    api = "core:submission-article7-exports-list"
    factory_klass = ExportFactory


class DestructionDataCheckCreate(BaseDataCreateRemarksTestsMixIn, TestCase):
    api = "core:submission-article7-destructions-list"


class DestructionDataCheckUpdate(BaseDataUpdateRemarksTestsMixIn, TestCase):
    api = "core:submission-article7-destructions-list"
    factory_klass = DestructionFactory


class ProductionDataCheckCreate(BaseDataCreateRemarksTestsMixIn, TestCase):
    api = "core:submission-article7-productions-list"


class ProductionDataCheckUpdate(BaseDataUpdateRemarksTestsMixIn, TestCase):
    api = "core:submission-article7-productions-list"
    factory_klass = ProductionFactory


class EmissionDataCheckCreate(BaseDataCreateRemarksTestsMixIn, TestCase):
    api = "core:submission-article7-emissions-list"
    api_data = {"facility_name": "Test Facility", "quantity_emitted": 10}
    no_substance = True


class EmissionDataCheckUpdate(BaseDataUpdateRemarksTestsMixIn, TestCase):
    api = "core:submission-article7-emissions-list"
    api_data = {"facility_name": "Test Facility", "quantity_emitted": 10}
    factory_klass = EmissionFactory
    no_substance = True


class NonPartyTradeDataCheckCreate(BaseDataCreateRemarksTestsMixIn, TestCase):
    api = "core:submission-article7-nonpartytrades-list"
    api_data = {"quantity_import_new": 42}


class NonPartyTradeDataCheckUpdate(BaseDataUpdateRemarksTestsMixIn, TestCase):
    api = "core:submission-article7-nonpartytrades-list"
    api_data = {"quantity_import_new": 42}
    factory_klass = NonPartyTradeFactory


class HighAmbientTemperatureImportCheckCreate(BaseDataCreateRemarksTestsMixIn, TestCase):
    api = "core:submission-hat-imports-list"


class HighAmbientTemperatureImportCheckUpdate(BaseDataUpdateRemarksTestsMixIn, TestCase):
    api = "core:submission-hat-imports-list"
    factory_klass = HighAmbientTemperatureImportFactory


class HighAmbientTemperatureProductionCheckCreate(BaseDataCreateRemarksTestsMixIn, TestCase):
    api = "core:submission-hat-productions-list"


class HighAmbientTemperatureProductionCheckUpdate(BaseDataUpdateRemarksTestsMixIn, TestCase):
    api = "core:submission-hat-productions-list"
    factory_klass = HighAmbientTemperatureProductionFactory
