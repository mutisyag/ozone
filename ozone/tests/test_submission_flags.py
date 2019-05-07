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
    LanguageEnFactory,
    ReporterUserFactory,
    ReportingChannelFactory,
    SecretariatUserFactory,
    SubmissionFactory,
    SubregionFactory,
)

User = get_user_model()


NEW_VALUE = True
OLD_VALUE = False


class BaseFlagsTests(BaseTests):
    success_code = 200
    fail_code = 422
    _form_type = "art7"
    flag_data = {}

    def setUp(self):
        super().setUp()
        self.workflow_class = "default"

        self.obligation = ObligationFactory(_form_type=self._form_type)
        self.region = RegionFactory.create()
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
        self.another_party_user = ReporterUserFactory(
            language=self.language,
            username="another-reporter",
            party=self.another_party,
            password=hash_alg.encode(password="qwe123qwe", salt="123salt123"),
        )
        ReportingChannelFactory()

    def create_submission(self, owner, **kwargs):
        submission = SubmissionFactory(
            party=self.party, created_by=owner, last_edited_by=owner,
            obligation=self.obligation,
            **kwargs
        )
        return submission

    def _check_result(
        self, result, expect_success, submission, field, fail_code=None
    ):
        try:
            verbose = result.json()
        except:
            verbose = result.data

        # If fail_code not specified as parameter, use class attribute
        fail_code = fail_code if fail_code is not None else self.fail_code
        self.assertEqual(
            result.status_code,
            self.success_code if expect_success else fail_code,
            verbose,
        )

        submission = Submission.objects.get(pk=submission.id)

        expected_value = OLD_VALUE
        # If the field we are trying to change is not available
        # for the obligation type, we don't raise an error, but the
        # value doesn't actually change.
        if expect_success and field in self.flag_data:
            expected_value = NEW_VALUE

        self.assertEqual(getattr(submission, field), expected_value)


BLANKS_FLAGS = (
    'flag_checked_blanks',
    'flag_has_blanks',
    'flag_confirmed_blanks',
)

# flag_confirmed_blanks can only be True if flag_checked_blanks is True
FLAGS_DEPENDENCY = {
    'flag_confirmed_blanks': 'flag_checked_blanks'
}

HAS_REPORTED_FLAGS = (
    'flag_has_reported_a1', 'flag_has_reported_a2',
    'flag_has_reported_b1', 'flag_has_reported_b2',
    'flag_has_reported_b3', 'flag_has_reported_c1',
    'flag_has_reported_c2', 'flag_has_reported_c3',
    'flag_has_reported_e', 'flag_has_reported_f',
)
PROVISIONAL_FLAGS = (
    'flag_provisional',
)
VALID_FLAGS = (
    'flag_valid',
)
SUPERSEDED_FLAGS = (
    'flag_superseded',
)
EXEMPTION_FLAGS = (
    'flag_approved',
    'flag_emergency',
)

ALL_FLAGS = BLANKS_FLAGS + HAS_REPORTED_FLAGS + PROVISIONAL_FLAGS + VALID_FLAGS + SUPERSEDED_FLAGS
ALL_FLAGS_DATA = {
    _flag: OLD_VALUE for _flag in ALL_FLAGS
}
BASE_FLAG_DATA = {
    _flag: OLD_VALUE for _flag in SUPERSEDED_FLAGS + VALID_FLAGS + PROVISIONAL_FLAGS
}
BLANKS_FLAGS_DATA = {
    _flag: OLD_VALUE for _flag in BLANKS_FLAGS
}
HAS_REPORTED_FLAGS_DATA = {
    _flag: OLD_VALUE for _flag in HAS_REPORTED_FLAGS
}
ESSENCRIT_FLAGS_DATA = {
    _flag: OLD_VALUE for _flag in PROVISIONAL_FLAGS + VALID_FLAGS + SUPERSEDED_FLAGS
}
EXEMPTION_FLAGS_DATA = {
    _flag: OLD_VALUE for _flag in EXEMPTION_FLAGS
}


class SubmissionFlagsPermissionTests(BaseFlagsTests):
    flag_data = ALL_FLAGS_DATA

    def _check_flags_update_permission(
        self, user, fields_to_check, finalized, expect_success, fail_code=None
    ):
        fields_to_check = list(
            set(fields_to_check) & set(self.flag_data.keys())
        )
        if not fields_to_check:
            return

        submission = self.create_submission(
            self.secretariat_user, **ALL_FLAGS_DATA
        )
        if finalized:
            submission.call_transition("finalize", self.secretariat_user)
            submission.save()
        self.client.login(username=user.username, password='qwe123qwe')

        for field in fields_to_check:
            with self.subTest("Test update %s" % field):
                if field in FLAGS_DEPENDENCY.keys():
                    # Flag has a dependency; should not update without it, error
                    # should be 422 if success was expected, fail_code otherwise

                    # Set dependency flag to False just to be sure
                    self.client.put(
                        reverse(
                            "core:submission-submission-flags-list",
                            kwargs={"submission_pk": submission.pk},
                        ),
                        {FLAGS_DEPENDENCY[field]: False},
                    )

                    # Try to set dependent flag
                    result = self.client.put(
                        reverse(
                            "core:submission-submission-flags-list",
                            kwargs={"submission_pk": submission.pk},
                        ),
                        {field: NEW_VALUE},
                    )
                    self._check_result(
                        result, False, submission, field,
                        422 if expect_success else fail_code
                    )

                    # Now try to first set flag it depends on to True, then
                    # result should be as expected.
                    self.client.put(
                        reverse(
                            "core:submission-submission-flags-list",
                            kwargs={"submission_pk": submission.pk},
                        ),
                        {FLAGS_DEPENDENCY[field]: True},
                    )

                result = self.client.put(
                    reverse(
                        "core:submission-submission-flags-list",
                        kwargs={"submission_pk": submission.pk},
                    ),
                    {field: NEW_VALUE},
                )
                self._check_result(
                    result, expect_success, submission, field, fail_code
                )

    # Superseded flags cannot be change by any user in any state

    def test_superseded_secretariat_data_entry(self):
        self._check_flags_update_permission(
            self.secretariat_user, SUPERSEDED_FLAGS, False, False
        )

    def test_superseded_secretariat_finalized(self):
        self._check_flags_update_permission(
            self.secretariat_user, SUPERSEDED_FLAGS, True, False
        )

    def test_superseded_party_data_entry(self):
        # fail_code is 403 as party user has no permission to change flags
        # on secretariat-created submissions
        self._check_flags_update_permission(
            self.party_user, SUPERSEDED_FLAGS, False, False, fail_code=403
        )

    def test_superseded_party_finalized(self):
        # fail_code is 403 as party user has no permission to change flags
        # on secretariat-created submissions
        self._check_flags_update_permission(
            self.party_user, SUPERSEDED_FLAGS, True, False, fail_code=403
        )

    # Provisional flag can be edited by:
    #  - Secretariat in any state
    #  - Party in data entry

    def test_provisional_secretariat_data_entry(self):
        self._check_flags_update_permission(
            self.secretariat_user, PROVISIONAL_FLAGS, False, True
        )

    def test_provisional_secretariat_finalized(self):
        self._check_flags_update_permission(
            self.secretariat_user, PROVISIONAL_FLAGS, True, True
        )

    def test_provisional_party_data_entry(self):
        # fail_code is 403 as party user has no permission to change flags
        # on secretariat-created submissions
        self._check_flags_update_permission(
            self.party_user, PROVISIONAL_FLAGS, False, False, fail_code=403
        )

    def test_provisional_party_finalized(self):
        # fail_code is 403 as party user has no permission to change flags
        # on secretariat-created submissions
        self._check_flags_update_permission(
            self.party_user, PROVISIONAL_FLAGS, True, False, fail_code=403
        )

    # Valid flag can be edited by:
    #  - Secretariat in submitted, processing & finalized states
    #  - Party in no state

    def test_valid_secretariat_data_entry(self):
        self._check_flags_update_permission(
            self.secretariat_user, VALID_FLAGS, False, False
        )

    def test_valid_secretariat_finalized(self):
        self._check_flags_update_permission(
            self.secretariat_user, VALID_FLAGS, True, True
        )

    def test_valid_party_data_entry(self):
        self._check_flags_update_permission(
            self.party_user, VALID_FLAGS, False, False, fail_code=403
        )

    def test_valid_party_finalized(self):
        self._check_flags_update_permission(
            self.party_user, VALID_FLAGS, True, False, fail_code=403
        )

    # Blanks can be edited by:
    #  - Secretariat in any state
    #  - Party in no state

    def test_blanks_secretariat_data_entry(self):
        self._check_flags_update_permission(
            self.secretariat_user, BLANKS_FLAGS, False, True
        )

    def test_blanks_secretariat_finalized(self):
        self._check_flags_update_permission(
            self.secretariat_user, BLANKS_FLAGS, True, True
        )

    def test_blanks_party_data_entry(self):
        self._check_flags_update_permission(
            self.party_user, BLANKS_FLAGS, False, False, fail_code=403
        )

    def test_blanks_party_finalized(self):
        self._check_flags_update_permission(
            self.party_user, BLANKS_FLAGS, True, False, fail_code=403
        )

    # Has reported flags can be edited by:
    #  - Secretariat in data entry state
    #  - Party in data entry state

    def test_has_reported_secretariat_data_entry(self):
        self._check_flags_update_permission(
            self.secretariat_user, HAS_REPORTED_FLAGS, False, True
        )

    def test_has_reported_secretariat_finalized(self):
        self._check_flags_update_permission(
            self.secretariat_user, HAS_REPORTED_FLAGS, True, False
        )

    def test_has_reported_party_data_entry(self):
        self._check_flags_update_permission(
            self.party_user, HAS_REPORTED_FLAGS, False, False, fail_code=403
        )

    def test_has_reported_party_finalized(self):
        self._check_flags_update_permission(
            self.party_user, HAS_REPORTED_FLAGS, True, False, fail_code=403
        )


class HATSubmissionFlagsPermissionTests(SubmissionFlagsPermissionTests):
    flag_data = ALL_FLAGS_DATA
    _form_type = "hat"


class EssenCritSubmissionFlagsPermissionTests(SubmissionFlagsPermissionTests):
    flag_data = ESSENCRIT_FLAGS_DATA
    _form_type = "essencrit"


class OtherSubmissionFlagsPermissionTests(SubmissionFlagsPermissionTests):
    flag_data = BASE_FLAG_DATA
    _form_type = "other"


class ExemptionSubmissionFlagsPermissionTests(SubmissionFlagsPermissionTests):
    flag_data = EXEMPTION_FLAGS_DATA
    _form_type = "exemption"


class SubmissionRetrieveTest(BaseFlagsTests):
    flag_data = ALL_FLAGS_DATA

    def _check_flags_retrieve_data(self, user, owner):
        submission = self.create_submission(owner, **self.flag_data)
        self.client.login(username=user.username, password='qwe123qwe')

        result = self.client.get(
            reverse(
                "core:submission-submission-flags-list",
                kwargs={"submission_pk": submission.pk},
            ),
        )
        self.assertEqual(result.json(), [self.flag_data])

    def test_retrieve_as_party_party_reporter(self):
        self._check_flags_retrieve_data(self.party_user, self.party_user)

    def test_retrieve_as_party_secretariat_reporter(self):
        self._check_flags_retrieve_data(self.party_user, self.secretariat_user)

    def test_retrieve_as_secretariat_party_reporter(self):
        self._check_flags_retrieve_data(self.secretariat_user, self.party_user)

    def test_retrieve_as_secretariat_secretariat_reporter(self):
        self._check_flags_retrieve_data(
            self.secretariat_user, self.secretariat_user
        )


class HATSubmissionRetrieveTest(SubmissionRetrieveTest):
    flag_data = ALL_FLAGS_DATA
    _form_type = "hat"


class EssenCritSubmissionRetrieveTest(SubmissionRetrieveTest):
    flag_data = ESSENCRIT_FLAGS_DATA
    _form_type = "essencrit"


class OtherSubmissionRetrieveTest(SubmissionRetrieveTest):
    flag_data = BASE_FLAG_DATA
    _form_type = "other"


class ExemptionSubmissionRetrieveTest(SubmissionRetrieveTest):
    flag_data = EXEMPTION_FLAGS_DATA
    _form_type = "exemption"
