import unittest

from django.urls import reverse
from django.contrib.auth.hashers import Argon2PasswordHasher

from ozone.core.models import Article7Import, Submission

from .base import BaseTests
from .factories import (
    PartyFactory,
    RegionFactory,
    ReporterUserFactory,
    ReportingChannelFactory,
    SecretariatUserFactory,
    SubmissionFactory,
    ObligationFactory,
    SubregionFactory,
    SubstanceFactory,
    AnotherSubstanceFactory,
    AnotherPartyFactory,
    ImportFactory,
)


class BaseArt7ImportTest(BaseTests):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.workflow_class = "default"

        self.obligation = ObligationFactory(_form_type="art7")
        self.region = RegionFactory.create()
        self.subregion = SubregionFactory.create(region=self.region)
        self.party = PartyFactory(subregion=self.subregion)
        self.another_party = AnotherPartyFactory(subregion=self.subregion)

        hash_alg = Argon2PasswordHasher()
        self.secretariat_user = SecretariatUserFactory(
            password=hash_alg.encode(password="qwe123qwe", salt="123salt123")
        )
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')

        self.substance = SubstanceFactory()
        self.another_substance = AnotherSubstanceFactory()
        ReportingChannelFactory()

    def create_submission(self, **kwargs):
        if "obligation" not in kwargs:
            kwargs["obligation"] = self.obligation

        submission = SubmissionFactory(
            party=self.party, created_by=self.secretariat_user,
            last_edited_by=self.secretariat_user, **kwargs
        )
        return submission


ART7_IMPORT_DATA = {
    'decision_critical_uses': '',
    'decision_essential_uses': '',
    'decision_high_ambient_temperature': '',
    'decision_laboratory_analytical_uses': '',
    'decision_other_uses': '',
    'decision_process_agent_uses': '',
    'decision_quarantine_pre_shipment': '',
    'quantity_critical_uses': None,
    'quantity_essential_uses': None,
    'quantity_feedstock': None,
    'quantity_high_ambient_temperature': None,
    'quantity_laboratory_analytical_uses': None,
    'quantity_other_uses': None,
    'quantity_polyols': None,
    'quantity_process_agent_uses': None,
    'quantity_quarantine_pre_shipment': None,
    'quantity_total_new': 40.0,
    'quantity_total_recovered': None,
    'remarks_os': 'nothing to remark OS',
    'remarks_party': 'nothing to remark',
}


class TestArt7Import(BaseArt7ImportTest):

    def test_create(self):
        submission = self.create_submission()

        data = dict(ART7_IMPORT_DATA)
        data["substance"] = self.substance.id

        result = self.client.post(
            reverse(
                "core:submission-article7-imports-list",
                kwargs={"submission_pk": submission.pk},
            ),
            [data],
        )
        self.assertEqual(result.status_code, 201, result.json())

    def test_create_wrong_obligation(self):
        obligation = ObligationFactory.create(_form_type="hat", name="Much obliged")
        submission = self.create_submission(obligation=obligation)

        data = dict(ART7_IMPORT_DATA)
        data["substance"] = self.substance.id

        result = self.client.post(
            reverse(
                "core:submission-article7-imports-list",
                kwargs={"submission_pk": submission.pk},
            ),
            [data],
        )
        self.assertEqual(result.status_code, 403, result.json())

    def test_create_multiple(self):
        submission = self.create_submission()

        data1 = dict(ART7_IMPORT_DATA)
        data1["substance"] = self.substance.id

        data2 = dict(ART7_IMPORT_DATA)
        data2["substance"] = self.another_substance.id

        result = self.client.post(
            reverse(
                "core:submission-article7-imports-list",
                kwargs={"submission_pk": submission.pk},
            ),
            [data1, data2],
        )
        self.assertEqual(result.status_code, 201, result.json())

    def test_create_multiple_duplicate(self):
        submission = self.create_submission()

        data1 = dict(ART7_IMPORT_DATA)
        data1["substance"] = self.substance.id

        data2 = dict(ART7_IMPORT_DATA)
        data2["substance"] = self.substance.id

        result = self.client.post(
            reverse(
                "core:submission-article7-imports-list",
                kwargs={"submission_pk": submission.pk},
            ),
            [data1, data2],
        )
        self.assertEqual(result.status_code, 422, result.json())

    def test_create_multiple_source_party(self):
        submission = self.create_submission()

        data1 = dict(ART7_IMPORT_DATA)
        data1["substance"] = self.substance.id
        data1["source_party"] = self.party.id

        data2 = dict(ART7_IMPORT_DATA)
        data2["substance"] = self.substance.id
        data2["source_party"] = self.another_party.id

        result = self.client.post(
            reverse(
                "core:submission-article7-imports-list",
                kwargs={"submission_pk": submission.pk},
            ),
            [data1, data2],
        )
        self.assertEqual(result.status_code, 201, result.json())

    def test_create_multiple_source_party_duplicate(self):
        submission = self.create_submission()

        data1 = dict(ART7_IMPORT_DATA)
        data1["substance"] = self.substance.id
        data1["source_party"] = self.party.id

        data2 = dict(ART7_IMPORT_DATA)
        data2["substance"] = self.substance.id
        data2["source_party"] = self.party.id

        result = self.client.post(
            reverse(
                "core:submission-article7-imports-list",
                kwargs={"submission_pk": submission.pk},
            ),
            [data1, data2],
        )
        self.assertEqual(result.status_code, 422, result.json())

    def test_get(self):
        submission = self.create_submission()

        art7_import = ImportFactory(
            submission=submission, substance=self.substance,
            **ART7_IMPORT_DATA
        )

        result = self.client.get(
            reverse(
                "core:submission-article7-imports-list",
                kwargs={"submission_pk": submission.pk},
            ),
        )
        self.assertEqual(result.status_code, 200, result.json())

        expected_data = dict(ART7_IMPORT_DATA)
        expected_data["substance"] = self.substance.id
        expected_data["blend"] = None
        expected_data["derived_substance_data"] = []
        expected_data["id"] = art7_import.id
        expected_data["ordering_id"] = 0
        expected_data["group"] = ''
        expected_data["source_party"] = None
        self.assertEqual(result.json(), [expected_data])

    def test_update(self):
        submission = self.create_submission()

        art7_import = ImportFactory(
            submission=submission, substance=self.substance,
            **ART7_IMPORT_DATA
        )

        data = dict(ART7_IMPORT_DATA)
        data["substance"] = self.substance.id
        data["quantity_total_new"] = 42

        result = self.client.put(
            reverse(
                "core:submission-article7-imports-list",
                kwargs={"submission_pk": submission.pk},
            ),
            [data],
        )
        self.assertEqual(result.status_code, 200, result.json())

        art7_import = Article7Import.objects.get(pk=art7_import.id)
        self.assertEqual(art7_import.quantity_total_new, 42)

    def test_update_multiple(self):
        submission = self.create_submission()

        art7_import = ImportFactory(
            submission=submission, substance=self.substance,
            **ART7_IMPORT_DATA
        )

        data1 = dict(ART7_IMPORT_DATA)
        data1["substance"] = self.substance.id
        data1["quantity_total_new"] = 42

        data2 = dict(ART7_IMPORT_DATA)
        data2["substance"] = self.another_substance.id
        data2["quantity_total_new"] = 42

        result = self.client.put(
            reverse(
                "core:submission-article7-imports-list",
                kwargs={"submission_pk": submission.pk},
            ),
            [data1, data2],
        )
        self.assertEqual(result.status_code, 200, result.json())

        art7_import1 = submission.article7imports.get(
            substance_id=self.substance.id
        )
        art7_import2 = submission.article7imports.get(
            substance_id=self.another_substance.id
        )
        self.assertEqual(art7_import1.quantity_total_new, 42)
        self.assertEqual(art7_import2.quantity_total_new, 42)

    def test_update_multiple_duplicate(self):
        submission = self.create_submission()

        art7_import = ImportFactory(
            submission=submission, substance=self.substance,
            **ART7_IMPORT_DATA
        )

        data1 = dict(ART7_IMPORT_DATA)
        data1["substance"] = self.substance.id
        data1["quantity_total_new"] = 42

        data2 = dict(ART7_IMPORT_DATA)
        data2["substance"] = self.substance.id
        data2["quantity_total_new"] = 42

        result = self.client.put(
            reverse(
                "core:submission-article7-imports-list",
                kwargs={"submission_pk": submission.pk},
            ),
            [data1, data2],
        )
        self.assertEqual(result.status_code, 422, result.json())

    def test_update_multiple_source_party(self):
        submission = self.create_submission()

        art7_import = ImportFactory(
            submission=submission, substance=self.substance,
            source_party=self.party,
            **ART7_IMPORT_DATA
        )

        data1 = dict(ART7_IMPORT_DATA)
        data1["substance"] = self.substance.id
        data1["source_party"] = self.party.id
        data1["quantity_total_new"] = 42

        data2 = dict(ART7_IMPORT_DATA)
        data2["substance"] = self.substance.id
        data2["source_party"] = self.another_party.id
        data2["quantity_total_new"] = 42

        result = self.client.put(
            reverse(
                "core:submission-article7-imports-list",
                kwargs={"submission_pk": submission.pk},
            ),
            [data1, data2],
        )
        self.assertEqual(result.status_code, 200, result.json())

        art7_import1 = submission.article7imports.get(
            substance_id=self.substance.id, source_party=self.party,
        )
        art7_import2 = submission.article7imports.get(
            substance_id=self.substance.id, source_party=self.another_party,
        )
        self.assertEqual(art7_import1.quantity_total_new, 42)
        self.assertEqual(art7_import2.quantity_total_new, 42)

    def test_update_multiple_source_party_duplicate(self):
        submission = self.create_submission()

        art7_import = ImportFactory(
            submission=submission, substance=self.substance,
            source_party=self.party,
            **ART7_IMPORT_DATA
        )

        data1 = dict(ART7_IMPORT_DATA)
        data1["substance"] = self.substance.id
        data1["source_party"] = self.party.id
        data1["quantity_total_new"] = 42

        data2 = dict(ART7_IMPORT_DATA)
        data2["substance"] = self.substance.id
        data2["source_party"] = self.party.id
        data2["quantity_total_new"] = 42

        result = self.client.put(
            reverse(
                "core:submission-article7-imports-list",
                kwargs={"submission_pk": submission.pk},
            ),
            [data1, data2],
        )
        self.assertEqual(result.status_code, 422, result.json())

    def test_update_immutable(self):
        submission = self.create_submission()

        art7_import = ImportFactory(
            submission=submission, substance=self.substance,
            **ART7_IMPORT_DATA
        )
        submission.call_transition("submit", self.secretariat_user)
        submission.save()

        data = dict(ART7_IMPORT_DATA)
        data["substance"] = self.substance.id
        data["quantity_total_new"] = 41
        result = self.client.put(
            reverse(
                "core:submission-article7-imports-list",
                kwargs={"submission_pk": submission.pk},
            ),
            [data],
        )
        self.assertEqual(result.status_code, 422, result.json())

    def test_clone(self):
        submission = self.create_submission()

        art7_import = ImportFactory(
            submission=submission, substance=self.substance,
            **ART7_IMPORT_DATA
        )
        submission._current_state = "finalized"
        submission.save()

        result = self.client.post(
            reverse(
                "core:submission-clone",
                kwargs={"pk": submission.pk},
            ),
        )
        self.assertEqual(result.status_code, 200, result.json())
        new_id = result.json()['url'].split("/")[-2]

        new_art7 = Submission.objects.get(pk=new_id).article7imports.first()
        self.assertEqual({
            'quantity_total_new': new_art7.quantity_total_new,
            'remarks_os': new_art7.remarks_os,
            'remarks_party': new_art7.remarks_party,
        }, {
            'quantity_total_new': ART7_IMPORT_DATA['quantity_total_new'],
            'remarks_os': ART7_IMPORT_DATA['remarks_os'],
            'remarks_party': ART7_IMPORT_DATA['remarks_party'],
        })
