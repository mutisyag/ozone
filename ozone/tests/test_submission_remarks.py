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

    def create_submission(self, owner, **kwargs):
        submission = SubmissionFactory(
            party=self.party, created_by=owner, last_edited_by=owner, **kwargs
        )
        return submission


class SubmissionRemarksPermissionTests(BaseRemarksTests):
    """Checks editable permission depending on:
        - user type who is changing the field
        - the type of the field (either party or secretariat remark)
        - user type who reported the submission
    """

    def _check_remark_update_permission(self, user, field, owner, expect_success):
        # XXX Assume this works correctly for all other fields.
        field = "imports_remarks_%s" % field

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
            **headers,
        )
        self.assertEqual(result.status_code == 200, expect_success)

    def test_party_user_party_field_party_reporter(self):
        self._check_remark_update_permission(
            self.party_user, "party", self.party_user, True
        )

    def test_party_user_party_filed_secretariat_reporter(self):
        self._check_remark_update_permission(
            self.party_user, "party", self.secretariat_user, True
        )

    def test_party_user_secretariat_field_party_reporter(self):
        self._check_remark_update_permission(
            self.party_user, "secretariat", self.party_user, False
        )

    def test_party_user_secretariat_field_secretariat_reporter(self):
        self._check_remark_update_permission(
            self.party_user, "secretariat", self.secretariat_user, False
        )

    def test_secretariat_user_party_field_party_reporter(self):
        self._check_remark_update_permission(
            self.secretariat_user, "party", self.party_user, False
        )

    def test_secretariat_user_party_field_secretariat_reporter(self):
        self._check_remark_update_permission(
            self.secretariat_user, "party", self.secretariat_user, True
        )

    def test_secretariat_user_secretariat_field_party_reporter(self):
        self._check_remark_update_permission(
            self.secretariat_user, "secretariat", self.party_user, True
        )

    def test_secretariat_user_secretariat_field_secretariat_reporter(self):
        self._check_remark_update_permission(
            self.secretariat_user, "secretariat", self.secretariat_user, True
        )


class SubmissionRemarksPermissionWorkflowTests(BaseRemarksTests):
    """Checks editable permission depending on:

     - workflow state
     - field type
    """

    def _check_remark_update_permission_state(
        self, user, field, owner, previous_state, current_state, expect_success
    ):
        # XXX Assume this works correctly for all other fields.
        field = "imports_remarks_%s" % field

        submission = self.create_submission(owner)
        submission._previous_state = previous_state
        submission._current_state = current_state
        submission.flag_valid = True
        submission.save()

        headers = self.get_authorization_header(user.username, "qwe123qwe")

        result = self.client.put(
            reverse(
                "core:submission-submission-remarks-list",
                kwargs={"submission_pk": submission.pk},
            ),
            {field: "Some random remark here."},
            "application/json",
            format="json",
            **headers,
        )
        self.assertEqual(result.status_code == 200, expect_success)

    def test_modify_party_field_in_data_entry_by_party_user(self):
        self._check_remark_update_permission_state(
            self.party_user, "party", self.party_user, None, "data_entry", True
        )

    def test_modify_party_field_in_data_entry_by_secretariat_user(self):
        self._check_remark_update_permission_state(
            self.secretariat_user,
            "party",
            self.secretariat_user,
            None,
            "data_entry",
            True,
        )

    def test_modify_party_field_in_submitted_by_party_user(self):
        self._check_remark_update_permission_state(
            self.party_user, "party", self.party_user, "data_entry", "submitted", False
        )

    def test_modify_party_field_in_submitted_by_secretariat_user(self):
        self._check_remark_update_permission_state(
            self.secretariat_user,
            "party",
            self.party_user,
            "data_entry",
            "submitted",
            False,
        )

    def test_modify_secretariat_field_in_data_entry_by_secretariat_user(self):
        self._check_remark_update_permission_state(
            self.secretariat_user,
            "secretariat",
            self.party_user,
            None,
            "data_entry",
            True,
        )

    def test_modify_secretariat_field_in_submitted_by_secretariat_user(self):
        self._check_remark_update_permission_state(
            self.secretariat_user,
            "secretariat",
            self.party_user,
            "data_entry",
            "submitted",
            True,
        )


remarks_data = {
    "imports_remarks_party": "Testing",
    "imports_remarks_secretariat": "Testing",
    "exports_remarks_party": "Testing",
    "exports_remarks_secretariat": "Testing",
    "production_remarks_party": "Testing",
    "production_remarks_secretariat": "Testing",
    "destruction_remarks_party": "Testing",
    "destruction_remarks_secretariat": "Testing",
    "nonparty_remarks_party": "Testing",
    "nonparty_remarks_secretariat": "Testing",
    "emissions_remarks_party": "Testing",
    "emissions_remarks_secretariat": "Testing",
}


class SubmissionRetrieveTest(BaseRemarksTests):
    def _check_remark_retrieve_data(self, user, owner):
        submission = self.create_submission(owner, **remarks_data)
        headers = self.get_authorization_header(user.username, "qwe123qwe")

        result = self.client.get(
            reverse(
                "core:submission-submission-remarks-list",
                kwargs={"submission_pk": submission.pk},
            ),
            format="json",
            **headers,
        )
        self.assertEqual(result.json(), [remarks_data])

    def test_retrieve_as_party_party_reporter(self):
        self._check_remark_retrieve_data(self.party_user, self.party_user)

    def test_retrieve_as_party_secretariat_reporter(self):
        self._check_remark_retrieve_data(self.party_user, self.secretariat_user)

    def test_retrieve_as_secretariat_party_reporter(self):
        self._check_remark_retrieve_data(self.secretariat_user, self.party_user)

    def test_retrieve_as_secretariat_secretariat_reporter(self):
        self._check_remark_retrieve_data(self.secretariat_user, self.secretariat_user)
