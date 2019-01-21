from unittest.mock import patch

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import Argon2PasswordHasher

from ozone.core.models import Submission
from .base import BaseTests
from .factories import (
    PartyFactory,
    AnotherPartyFactory,
    RegionFactory,
    ReporterUserFactory,
    ReportingChannelFactory,
    SecretariatUserFactory,
    SubmissionFactory,
    SubregionFactory,
)

User = get_user_model()

REMARK_VALUE = "Some random remark here."


class BaseRemarksTests(BaseTests):

    success_code = 200
    fail_code = 422

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
        self.another_party_user = ReporterUserFactory(
            username="another-reporter",
            party=self.another_party,
            password=hash_alg.encode(password="qwe123qwe", salt="123salt123"),
        )
        ReportingChannelFactory()

    def create_submission(self, owner, **kwargs):
        submission = SubmissionFactory(
            party=self.party, created_by=owner, last_edited_by=owner, **kwargs
        )
        return submission

    def _check_result(self, result, expect_success, submission, field):
        try:
            verbose = result.json()
        except:
            verbose = result.data
        self.assertEqual(
            result.status_code,
            self.success_code if expect_success else self.fail_code,
            verbose,
        )

        submission = Submission.objects.get(pk=submission.id)
        self.assertEqual(getattr(submission, field), REMARK_VALUE if expect_success else '')


class PatchIsSamePartyMixIn(object):

    def setUp(self):
        super().setUp()
        # Patch IsSecretariatOrSameParty since we are testing `check_remarks` here
        # and the check is somewhat duplicated.
        patch("ozone.core.permissions.BaseIsSecretariatOrSameParty.has_permission",
              return_value=True).start()

    def tearDown(self):
        super().tearDown()
        patch.stopall()


class SubmissionRemarksPermissionTests(PatchIsSamePartyMixIn, BaseRemarksTests):
    """Checks editable permission depending on:
        - user type who is changing the field
        - the type of the field (either party or secretariat remark)
        - user type who reported the submission
    """

    def _check_remark_update_permission(self, user, field_type, owner, expect_success):
        submission = self.create_submission(owner)
        self.client.login(username=user.username, password='qwe123qwe')

        for field in remarks_data.keys():
            if not field.endswith(field_type):
                continue

            with self.subTest("Test update %s" % field):
                result = self.client.put(
                    reverse(
                        "core:submission-submission-remarks-list",
                        kwargs={"submission_pk": submission.pk},
                    ),
                    {field: REMARK_VALUE},
                )
                self._check_result(result, expect_success, submission, field)

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


class SubmissionRemarksPermissionWorkflowTests(PatchIsSamePartyMixIn, BaseRemarksTests):
    """Checks editable permission depending on:

     - workflow state
     - field type
    """

    def _check_remark_update_permission_state(
        self, user, field_type, owner, previous_state, current_state, expect_success
    ):
        submission = self.create_submission(owner)
        submission._previous_state = previous_state
        submission._current_state = current_state
        submission.flag_valid = True
        submission.save()

        self.client.login(username=user.username, password='qwe123qwe')

        for field in remarks_data.keys():
            if not field.endswith(field_type):
                continue
            with self.subTest("Test update state %s" % field):
                result = self.client.put(
                    reverse(
                        "core:submission-submission-remarks-list",
                        kwargs={"submission_pk": submission.pk},
                    ),
                    {field: REMARK_VALUE},
                )
                self._check_result(result, expect_success, submission, field)

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
    "hat_production_remarks_party": "Testing",
    "hat_production_remarks_secretariat": "Testing",
    "hat_imports_remarks_party": "Testing",
    "hat_imports_remarks_secretariat": "Testing",
}


class SubmissionRetrieveTest(BaseRemarksTests):
    def _check_remark_retrieve_data(self, user, owner):
        submission = self.create_submission(owner, **remarks_data)
        self.client.login(username=user.username, password='qwe123qwe')

        result = self.client.get(
            reverse(
                "core:submission-submission-remarks-list",
                kwargs={"submission_pk": submission.pk},
            ),
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
class SubmissionRemarksTestIsSamePartyPermissions(BaseRemarksTests):
    fail_code = 403

    def _check_remark_update_permission(self, user, field_type, owner, expect_success):
        submission = self.create_submission(owner)
        self.client.login(username=user.username, password='qwe123qwe')

        for field in remarks_data.keys():
            if not field.endswith(field_type):
                continue

            with self.subTest("Test update %s" % field):
                result = self.client.put(
                    reverse(
                        "core:submission-submission-remarks-list",
                        kwargs={"submission_pk": submission.pk},
                    ),
                    {field: REMARK_VALUE}
                )
                self._check_result(result, expect_success, submission, field)

    def _check_remark_retrieve_data(self, user, owner, expect_success):
        submission = self.create_submission(owner, **remarks_data)
        self.client.login(username=user.username, password='qwe123qwe')

        result = self.client.get(
            reverse(
                "core:submission-submission-remarks-list",
                kwargs={"submission_pk": submission.pk},
            )
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.json()), 1 if expect_success else 0)

    def test_get_same_party(self):
        self._check_remark_retrieve_data(self.party_user, self.party_user, True)

    def test_get_different_party(self):
        self._check_remark_retrieve_data(self.another_party_user, self.party_user, False)

    def test_get_secretariat(self):
        self._check_remark_retrieve_data(self.secretariat_user, self.party_user, True)

    def test_update_same_party(self):
        self._check_remark_update_permission(self.party_user, "party", self.party_user,
                                             True)

    def test_update_different_party(self):
        self._check_remark_update_permission(self.another_party_user, "party", self.party_user,
                                             False)

    def test_update_secretariat(self):
        self._check_remark_update_permission(self.secretariat_user, "secretariat", self.party_user,
                                             True)
