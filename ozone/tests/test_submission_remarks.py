from unittest.mock import patch

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import Argon2PasswordHasher

from ozone.core.models import Submission
from .base import BaseTests
from .factories import (
    ObligationFactory,
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
ART7_REMARKS_DATA = {
    "questionnaire_remarks_party": "Testing",
    "questionnaire_remarks_secretariat": "Testing",
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
HAT7_REMARKS_DATA = {
    "hat_production_remarks_party": "Testing",
    "hat_production_remarks_secretariat": "Testing",
    "hat_imports_remarks_party": "Testing",
    "hat_imports_remarks_secretariat": "Testing",
}
ESSENCRIT_REMARKS_DATA = {
    "raf_remarks_party": "Testing",
    "raf_remarks_secretariat": "Testing",
}
OTHER_REMARKS_DATA = {}
EXEMPTION_REMARKS_DATA = {
    "exemption_nomination_remarks_secretariat": "Testing",
    "exemption_approved_remarks_secretariat": "Testing",
}
ALL_REMARK_DATA = dict(
    **ART7_REMARKS_DATA,
    **HAT7_REMARKS_DATA,
    **ESSENCRIT_REMARKS_DATA,
    **OTHER_REMARKS_DATA,
    **EXEMPTION_REMARKS_DATA,
)


class BaseRemarksTests(BaseTests):
    success_code = 200
    fail_code = 422
    form_type = "art7"
    remarks_data = {}
    fail_on_wrong_field = False

    def setUp(self):
        super().setUp()
        self.workflow_class = "default"

        self.obligation = ObligationFactory(form_type=self.form_type)
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
            party=self.party,
            created_by=owner,
            last_edited_by=owner,
            obligation=self.obligation,
            **kwargs,
        )
        return submission

    def _check_result(self, result, expect_success, submission, field, fail_code=None):
        try:
            verbose = result.json()
        except:
            verbose = result.data

        # Use class attribute if parameter is None
        fail_code = fail_code if fail_code is not None else self.fail_code

        expected_code = self.success_code
        # If the field we are trying to change is not available
        # for the obligation type, we don't raise an error, but the
        # value doesn't actually change.
        if not expect_success and (field in self.remarks_data or self.fail_on_wrong_field):
            expected_code = fail_code

        self.assertEqual(result.status_code, expected_code, verbose)

        expected_value = ""
        # If the field we are trying to change is not available
        # for the obligation type, we don't raise an error, but the
        # value doesn't actually change.
        if expect_success and field in self.remarks_data:
            expected_value = REMARK_VALUE

        submission = Submission.objects.get(pk=submission.id)
        self.assertEqual(getattr(submission, field), expected_value)


class PatchIsSamePartyMixIn(object):

    def setUp(self):
        super().setUp()
        # Patch IsSecretariatOrSameParty since we are testing `check_remarks` here
        # and the check is somewhat duplicated.
        patch("ozone.core.permissions.IsSecretariatOrSamePartySubmissionRemarks.has_permission",
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

    remarks_data = ART7_REMARKS_DATA
    form_type = "art7"

    def _check_remark_update_permission(
        self, user, field_type, owner, expect_success, fail_code=None
    ):
        submission = self.create_submission(owner)
        self.client.login(username=user.username, password="qwe123qwe")

        for field in ALL_REMARK_DATA.keys():
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
                self._check_result(result, expect_success, submission, field, fail_code)

    def test_party_user_party_field_party_reporter(self):
        self._check_remark_update_permission(
            self.party_user, "party", self.party_user, True
        )

    def test_party_user_party_field_secretariat_reporter(self):
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


class HATSubmissionRemarksPermissionTests(SubmissionRemarksPermissionTests):
    remarks_data = HAT7_REMARKS_DATA
    form_type = "hat"


class EssenCritSubmissionRemarksPermissionTests(SubmissionRemarksPermissionTests):
    remarks_data = ESSENCRIT_REMARKS_DATA
    form_type = "essencrit"


class OtherSubmissionRemarksPermissionTests(SubmissionRemarksPermissionTests):
    remarks_data = OTHER_REMARKS_DATA
    form_type = "other"

class ExemptionSubmissionRemarksPermissionTests(
    SubmissionRemarksPermissionTests
):
    remarks_data = EXEMPTION_REMARKS_DATA
    form_type = "exemption"


class SubmissionRemarksPermissionWorkflowTests(
    PatchIsSamePartyMixIn, BaseRemarksTests
):
    """Checks editable permission depending on:

     - workflow state
     - field type
    """

    remarks_data = ART7_REMARKS_DATA
    form_type = "art7"

    def _check_remark_update_permission_state(
        self, user, field_type, owner, previous_state, current_state, expect_success
    ):
        submission = self.create_submission(owner)
        submission._previous_state = previous_state
        submission._current_state = current_state
        submission.flag_valid = True
        submission.save()

        self.client.login(username=user.username, password="qwe123qwe")

        for field in ALL_REMARK_DATA.keys():
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


class HATSubmissionRemarksPermissionWorkflowTests(
    SubmissionRemarksPermissionWorkflowTests
):
    remarks_data = HAT7_REMARKS_DATA
    form_type = "hat"


class EssenCritSubmissionRemarksPermissionWorkflowTests(
    SubmissionRemarksPermissionWorkflowTests
):
    remarks_data = ESSENCRIT_REMARKS_DATA
    form_type = "essencrit"


class OtherSubmissionRemarksPermissionWorkflowTests(
    SubmissionRemarksPermissionWorkflowTests
):
    remarks_data = OTHER_REMARKS_DATA
    form_type = "other"


class ExemptionSubmissionRemarksPermissionWorkflowTests(
    SubmissionRemarksPermissionWorkflowTests
):
    remarks_data = EXEMPTION_REMARKS_DATA
    form_type = "exemption"


class SubmissionRetrieveTest(BaseRemarksTests):
    remarks_data = ART7_REMARKS_DATA
    form_type = "art7"

    def _check_remark_retrieve_data(self, user, owner):
        submission = self.create_submission(owner, **ALL_REMARK_DATA)
        self.client.login(username=user.username, password="qwe123qwe")

        result = self.client.get(
            reverse(
                "core:submission-submission-remarks-list",
                kwargs={"submission_pk": submission.pk},
            )
        )
        self.assertEqual(result.json(), [self.remarks_data])

    def test_retrieve_as_party_party_reporter(self):
        self._check_remark_retrieve_data(self.party_user, self.party_user)

    def test_retrieve_as_party_secretariat_reporter(self):
        self._check_remark_retrieve_data(self.party_user, self.secretariat_user)

    def test_retrieve_as_secretariat_party_reporter(self):
        self._check_remark_retrieve_data(self.secretariat_user, self.party_user)

    def test_retrieve_as_secretariat_secretariat_reporter(self):
        self._check_remark_retrieve_data(self.secretariat_user, self.secretariat_user)


class HATSubmissionRetrieveTest(SubmissionRetrieveTest):
    remarks_data = HAT7_REMARKS_DATA
    form_type = "hat"


class EssenCritSubmissionRetrieveTest(SubmissionRetrieveTest):
    remarks_data = ESSENCRIT_REMARKS_DATA
    form_type = "essencrit"


class OtherSubmissionRetrieveTest(SubmissionRetrieveTest):
    remarks_data = OTHER_REMARKS_DATA
    form_type = "other"


class ExemptionSubmissionRetrieveTest(SubmissionRetrieveTest):
    remarks_data = EXEMPTION_REMARKS_DATA
    form_type = "exemption"


class SubmissionRemarksTestIsSamePartyPermissions(BaseRemarksTests):
    success_code = 200
    fail_code = 403
    form_type = "art7"
    remarks_data = ART7_REMARKS_DATA
    fail_on_wrong_field = True

    def _check_remark_update_permission(self, user, field_type, owner, expect_success):
        submission = self.create_submission(owner)
        self.client.login(username=user.username, password='qwe123qwe')

        for field in ALL_REMARK_DATA.keys():
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
        submission = self.create_submission(owner, **ALL_REMARK_DATA)
        self.client.login(username=user.username, password="qwe123qwe")

        result = self.client.get(
            reverse(
                "core:submission-submission-remarks-list",
                kwargs={"submission_pk": submission.pk},
            )
        )
        self.assertEqual(
            result.status_code,
            self.success_code if expect_success else self.fail_code
        )
        # Failures return json containing dict-based error info.
        self.assertEqual(type(result.json()), list if expect_success else dict)

    def test_get_same_party(self):
        self._check_remark_retrieve_data(self.party_user, self.party_user, True)

    def test_get_different_party(self):
        self._check_remark_retrieve_data(
            self.another_party_user, self.party_user, False
        )

    def test_get_secretariat(self):
        self._check_remark_retrieve_data(
            self.secretariat_user, self.party_user, True
        )

    def test_update_same_party(self):
        self._check_remark_update_permission(
            self.party_user, "party", self.party_user, True
        )

    def test_update_different_party(self):
        self._check_remark_update_permission(
            self.another_party_user, "party", self.party_user, False
        )

    def test_update_secretariat(self):
        self._check_remark_update_permission(
            self.secretariat_user, "secretariat", self.party_user, True
        )


class HATSubmissionRemarksTestIsSamePartyPermissions(
    SubmissionRemarksTestIsSamePartyPermissions
):
    form_type = "hat"
    remarks_data = HAT7_REMARKS_DATA


class EssenCritSubmissionRemarksTestIsSamePartyPermissions(
    SubmissionRemarksTestIsSamePartyPermissions
):
    form_type = "essencrit"
    remarks_data = ESSENCRIT_REMARKS_DATA


class OtherSubmissionRemarksTestIsSamePartyPermissions(
    SubmissionRemarksTestIsSamePartyPermissions
):
    form_type = "other"
    remarks_data = OTHER_REMARKS_DATA


class ExemptionSubmissionRemarksTestIsSamePartyPermissions(
    SubmissionRemarksTestIsSamePartyPermissions
):
    form_type = "exemption"
    remarks_data = EXEMPTION_REMARKS_DATA
