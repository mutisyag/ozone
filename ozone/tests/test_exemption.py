from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import Argon2PasswordHasher

from ozone.core.models import Submission, Nomination, ExemptionApproved

from .base import BaseTests
from .factories import (
    AnotherSubstanceFactory,
    ExemptionApprovedFactory,
    LanguageEnFactory,
    NominationFactory,
    PartyFactory,
    RegionFactory,
    ReporterUserFactory,
    ReportingChannelFactory,
    ObligationFactory,
    SecretariatUserFactory,
    SubmissionFactory,
    SubregionFactory,
    SubstanceFactory,
)

User = get_user_model()

EXEMPTION_NOMINATION_DATA = {
    "quantity": 100,
    "remarks_os": "nothing to remark OS",
}

EXEMPTION_APPROVED_DATA = {
    "quantity": 100,
    "remarks_os": "nothing to remark OS",
    "decision_approved": "it's a test",
    "approved_teap_amount": 100
}


class BaseExemptionTests(BaseTests):
    def setUp(self):
        super().setUp()
        self.workflow_class = "default_exemption"
        self.obligation = ObligationFactory(_form_type="exemption")
        self.region = RegionFactory.create()
        self.subregion = SubregionFactory.create(region=self.region)
        self.party = PartyFactory(subregion=self.subregion)
        self.language = LanguageEnFactory()

        hash_alg = Argon2PasswordHasher()
        self.secretariat_user = SecretariatUserFactory(
            language = self.language,
            password=hash_alg.encode(password="qwe123qwe", salt="123salt123")
        )
        self.reporter = ReporterUserFactory(
            language=self.language,
            party=self.party,
            password=hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        self.another_substance = AnotherSubstanceFactory()
        self.substance = SubstanceFactory()
        ReportingChannelFactory()

    def create_submission(self, **kwargs):
        if "obligation" not in kwargs:
            kwargs["obligation"] = self.obligation

        submission = SubmissionFactory(
            party=self.party, created_by=self.secretariat_user,
            last_edited_by=self.secretariat_user, **kwargs
        )
        return submission


class ExemptionNominationTests(BaseExemptionTests):

    def test_create_secretariat(self):
        submission = self.create_submission()

        data = dict(EXEMPTION_NOMINATION_DATA)
        data["substance"] = self.substance.id

        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        result = self.client.post(
            reverse(
                "core:submission-exemption-nomination-list",
                kwargs={"submission_pk": submission.pk},
            ),
            data,
        )
        self.assertEqual(result.status_code, 201)

    def test_create_reporter(self):
        submission = self.create_submission()

        data = dict(EXEMPTION_NOMINATION_DATA)
        data["substance"] = self.substance.id

        self.client.login(username=self.reporter.username, password='qwe123qwe')
        result = self.client.post(
            reverse(
                "core:submission-exemption-nomination-list",
                kwargs={"submission_pk": submission.pk},
            ),
            data,
        )
        self.assertEqual(result.status_code, 403)

    def test_create_wrong_obligation(self):
        obligation = ObligationFactory.create(_form_type="art7", name="Much obliged")
        submission = self.create_submission(obligation=obligation)

        data = dict(EXEMPTION_NOMINATION_DATA)
        data["substance"] = self.substance.id

        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        result = self.client.post(
            reverse(
                "core:submission-exemption-nomination-list",
                kwargs={"submission_pk": submission.pk},
            ),
            data,
        )
        self.assertEqual(result.status_code, 403)

    def test_get_secretariat(self):
        submission = self.create_submission()

        nomination = NominationFactory(
            submission=submission, substance=self.substance,
            **EXEMPTION_NOMINATION_DATA
        )

        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        result = self.client.get(
            reverse(
                "core:submission-exemption-nomination-list",
                kwargs={"submission_pk": submission.pk},
            ),
        )
        self.assertEqual(result.status_code, 200)
        expected_data = dict(EXEMPTION_NOMINATION_DATA)
        expected_data["id"] = nomination.id
        expected_data["substance"] = self.substance.id
        expected_data["ordering_id"] = 0
        expected_data["group"] = ''
        self.assertEqual(result.json(), [expected_data])

    def test_get_reporter(self):
        submission = self.create_submission()

        nomination = NominationFactory(
            submission=submission, substance=self.substance,
            **EXEMPTION_NOMINATION_DATA
        )

        self.client.login(username=self.reporter.username, password='qwe123qwe')
        result = self.client.get(
            reverse(
                "core:submission-exemption-nomination-list",
                kwargs={"submission_pk": submission.pk},
            ),
        )
        self.assertEqual(result.status_code, 200)
        expected_data = dict(EXEMPTION_NOMINATION_DATA)
        expected_data["id"] = nomination.id
        expected_data["substance"] = self.substance.id
        expected_data["ordering_id"] = 0
        expected_data["group"] = ''
        self.assertEqual(result.json(), [expected_data])

    def test_update_secretariat(self):
        submission = self.create_submission()

        nomination = NominationFactory(
            submission=submission, substance=self.substance,
            **EXEMPTION_NOMINATION_DATA
        )

        data = dict(EXEMPTION_NOMINATION_DATA)
        data["substance"] = self.substance.id
        data["quantity"] = 99

        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        result = self.client.put(
            reverse(
                "core:submission-exemption-nomination-detail",
                kwargs={"submission_pk": submission.pk, "pk": nomination.id},
            ),
            data
        )
        self.assertEqual(result.status_code, 200)
        nomination = Nomination.objects.get(pk=nomination.id)
        self.assertEqual(nomination.quantity, 99)

    def test_update_reporter(self):
        submission = self.create_submission()

        nomination = NominationFactory(
            submission=submission, substance=self.substance,
            **EXEMPTION_NOMINATION_DATA
        )

        data = dict(EXEMPTION_NOMINATION_DATA)
        data["substance"] = self.substance.id
        data["quantity"] = 99

        self.client.login(username=self.reporter.username, password='qwe123qwe')
        result = self.client.put(
            reverse(
                "core:submission-exemption-nomination-detail",
                kwargs={"submission_pk": submission.pk, "pk": nomination.id},
            ),
            data
        )
        self.assertEqual(result.status_code, 403)


class ExemptionApprovedTests(BaseExemptionTests):

    def test_create_secretariat(self):
        submission = self.create_submission()

        data = dict(EXEMPTION_APPROVED_DATA)
        data["substance"] = self.substance.id

        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        result = self.client.post(
            reverse(
                "core:submission-exemption-approved-list",
                kwargs={"submission_pk": submission.pk},
            ),
            data,
        )
        self.assertEqual(result.status_code, 201)

    def test_create_reporter(self):
        submission = self.create_submission()

        data = dict(EXEMPTION_APPROVED_DATA)
        data["substance"] = self.substance.id

        self.client.login(username=self.reporter.username, password='qwe123qwe')
        result = self.client.post(
            reverse(
                "core:submission-exemption-approved-list",
                kwargs={"submission_pk": submission.pk},
            ),
            data,
        )
        self.assertEqual(result.status_code, 403)

    def test_create_wrong_obligation(self):
        obligation = ObligationFactory.create(_form_type="art7", name="Much obliged")
        submission = self.create_submission(obligation=obligation)

        data = dict(EXEMPTION_APPROVED_DATA)
        data["substance"] = self.substance.id

        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        result = self.client.post(
            reverse(
                "core:submission-exemption-approved-list",
                kwargs={"submission_pk": submission.pk},
            ),
            data,
        )
        self.assertEqual(result.status_code, 403)

    def test_get_secretariat(self):
        submission = self.create_submission()

        exemption_approved = ExemptionApprovedFactory(
            submission=submission, substance=self.substance,
            **EXEMPTION_APPROVED_DATA
        )

        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        result = self.client.get(
            reverse(
                "core:submission-exemption-approved-list",
                kwargs={"submission_pk": submission.pk},
            ),
        )
        self.assertEqual(result.status_code, 200)
        expected_data = dict(EXEMPTION_APPROVED_DATA)
        expected_data["id"] = exemption_approved.id
        expected_data["substance"] = self.substance.id
        expected_data["ordering_id"] = 0
        expected_data["group"] = ''
        # Default value for emergency is False
        expected_data["is_emergency"] = False
        self.assertEqual(result.json(), [expected_data])

    def test_get_reporter(self):
        submission = self.create_submission()

        exemption_approved = ExemptionApprovedFactory(
            submission=submission, substance=self.substance,
            **EXEMPTION_APPROVED_DATA
        )

        self.client.login(username=self.reporter.username, password='qwe123qwe')
        result = self.client.get(
            reverse(
                "core:submission-exemption-approved-list",
                kwargs={"submission_pk": submission.pk},
            ),
        )
        self.assertEqual(result.status_code, 200)
        expected_data = dict(EXEMPTION_APPROVED_DATA)
        expected_data["id"] = exemption_approved.id
        expected_data["substance"] = self.substance.id
        expected_data["ordering_id"] = 0
        expected_data["group"] = ''
        # Default value for is_emergency is False
        expected_data["is_emergency"] = False
        self.assertEqual(result.json(), [expected_data])

    def test_update_secretariat(self):
        submission = self.create_submission()

        exemption_approved = ExemptionApprovedFactory(
            submission=submission, substance=self.substance,
            **EXEMPTION_APPROVED_DATA
        )

        data = dict(EXEMPTION_APPROVED_DATA)
        data["substance"] = self.substance.id
        data["quantity"] = 99
        data["decision_approved"] = "edited"

        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        result = self.client.put(
            reverse(
                "core:submission-exemption-approved-detail",
                kwargs={"submission_pk": submission.pk, "pk": exemption_approved.id},
            ),
            data
        )
        self.assertEqual(result.status_code, 200)
        exemption_approved = ExemptionApproved.objects.get(pk=exemption_approved.id)
        self.assertEqual(exemption_approved.quantity, 99)
        self.assertEqual(exemption_approved.decision_approved, "edited")

    def test_update_reporter(self):
        submission = self.create_submission()

        exemption_approved = ExemptionApprovedFactory(
            submission=submission, substance=self.substance,
            **EXEMPTION_APPROVED_DATA
        )

        data = dict(EXEMPTION_APPROVED_DATA)
        data["substance"] = self.substance.id
        data["quantity"] = 99
        data["decision_approved"] = "edited"

        self.client.login(username=self.reporter.username, password='qwe123qwe')
        result = self.client.put(
            reverse(
                "core:submission-exemption-approved-detail",
                kwargs={"submission_pk": submission.pk, "pk": exemption_approved.id},
            ),
            data
        )
        self.assertEqual(result.status_code, 403)

