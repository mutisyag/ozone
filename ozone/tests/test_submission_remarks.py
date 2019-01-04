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
)

User = get_user_model()


class BaseRemarksTests(TestCase):
    def setUp(self):
        super().setUp()
        self.workflow_class = "default"

        self.region = RegionFactory.create()
        self.subregion = SubregionFactory.create(region=self.region)
        self.party = PartyFactory(subregion=self.subregion)

        hash_alg = Argon2PasswordHasher()
        self.secretariat_user = SecretariatUserFactory(
            password=hash_alg.encode(password="qwe123qwe", salt="123salt123")
        )
        self.party_user = ReporterUserFactory(
            party=self.party,
            password=hash_alg.encode(password="qwe123qwe", salt="123salt123"),
        )
        ReportingChannelFactory()

    def get_authorization_header(self, username, password):
        resp = self.client.post(
            reverse("core:auth-token-list"),
            {"username": username, "password": password},
            format="json",
        )
        return {"HTTP_AUTHORIZATION": "Token " + resp.data["token"]}

    def create_submission(self, owner):
        submission = SubmissionFactory(
            party=self.party, created_by=owner, last_edited_by=owner
        )
        return submission


class SubmissionRemarksPermissionTests(BaseRemarksTests):
    def _check_remark_update_permission(self, user, field, owner, expect_success):
        user = self.party_user if user == "party" else self.secretariat_user
        field = "imports_remarks_%s" % field
        owner = self.party_user if owner == "party" else self.secretariat_user

        submission = self.create_submission(owner)
        headers = self.get_authorization_header(user.username, "qwe123qwe")

        result = self.client.put(
            reverse(
                "core:submission-submission-remarks-list",
                kwargs={"submission_pk": submission.pk},
            ),
            {field: "Some random remark here."},
            "application/json",
            format="json",
            **headers
        )
        self.assertEqual(result.status_code == 200, expect_success)

    def test_party_user_party_field_party_reporter(self):
        self._check_remark_update_permission("party", "party", "party", True),

    def test_party_user_party_filed_secretariat_reporter(self):
        self._check_remark_update_permission("party", "party", "secretariat", True),

    def test_party_user_secretariat_field_party_reporter(self):
        self._check_remark_update_permission("party", "secretariat", "party", False),

    def test_party_user_secretariat_field_secretariat_reporter(self):
        self._check_remark_update_permission(
            "party", "secretariat", "secretariat", False
        ),

    def test_secretariat_user_party_field_party_reporter(self):
        self._check_remark_update_permission("secretariat", "party", "party", False),

    def test_secretariat_user_party_field_secretariat_reporter(self):
        self._check_remark_update_permission(
            "secretariat", "party", "secretariat", True
        ),

    def test_secretariat_user_secretariat_field_party_reporter(self):
        self._check_remark_update_permission(
            "secretariat", "secretariat", "party", True
        ),

    def test_secretariat_user_secretariat_field_secretariat_reporter(self):
        self._check_remark_update_permission(
            "secretariat", "secretariat", "secretariat", True
        )
