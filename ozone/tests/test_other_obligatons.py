from django.urls import reverse
from django.contrib.auth.hashers import Argon2PasswordHasher

from ozone.core.models import Submission, DataOther

from .base import BaseTests
from .factories import (
    PartyFactory,
    RegionFactory,
    ReportingChannelFactory,
    SecretariatUserFactory,
    SubmissionFactory,
    SubregionFactory,
    ObligationFactory,
    DataOtherFactory,
)

REMARKS_DATA = {
    'remarks_os': 'nothing to remark OS',
    'remarks_party': 'nothing to remark'
}


class DataOtherTest(BaseTests):
    def setUp(self):
        super().setUp()
        self.region = RegionFactory.create()
        self.subregion = SubregionFactory.create(region=self.region)
        self.party = PartyFactory(subregion=self.subregion)

        hash_alg = Argon2PasswordHasher()
        self.secretariat_user = SecretariatUserFactory(
            password=hash_alg.encode(password="qwe123qwe", salt="123salt123")
        )
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')

        self.obligation = ObligationFactory(name="Other obligation", other=True,
                                            _form_type="other")
        ReportingChannelFactory()

    def create_submission(self, **kwargs):
        if "obligation" not in kwargs:
            kwargs["obligation"] = self.obligation

        submission = SubmissionFactory(
            party=self.party, created_by=self.secretariat_user,
            last_edited_by=self.secretariat_user, **kwargs
        )
        return submission

    def test_create(self):
        submission = self.create_submission()

        data = dict(REMARKS_DATA)

        result = self.client.post(
            reverse(
                "core:submission-data-others-list",
                kwargs={"submission_pk": submission.pk}
            ),
            data
        )

        self.assertEqual(result.status_code, 201)
        self.assertEqual(submission.obligation, self.obligation)

    def test_create_wrong_obligation(self):
        obligation = ObligationFactory.create(_form_type="art7", name="Much obliged")
        submission = self.create_submission(obligation=obligation)

        data = dict(REMARKS_DATA)

        result = self.client.post(
            reverse(
                "core:submission-data-others-list",
                kwargs={"submission_pk": submission.pk}
            ),
            data
        )

        self.assertEqual(result.status_code, 403)

    def test_get(self):
        submission = self.create_submission()

        data_other = DataOtherFactory(submission=submission, **REMARKS_DATA)

        result = self.client.get(
            reverse(
                "core:submission-data-others-list",
                kwargs={"submission_pk": submission.pk}
            )
        )
        self.assertEqual(result.status_code, 200)
        expected_data = dict(REMARKS_DATA)
        expected_data["id"] = data_other.id
        expected_data["ordering_id"] = data_other.ordering_id
        self.assertEqual(result.json(), [expected_data])

    def test_update(self):
        submission = self.create_submission()

        data_other = DataOtherFactory(submission=submission, **REMARKS_DATA)

        data = dict(REMARKS_DATA)
        data["remarks_os"] = "edited remarks OS"
        data["remarks_party"] = "edited remarks Party"

        result = self.client.put(
            reverse(
                "core:submission-data-others-detail",
                kwargs={"submission_pk": submission.pk, "pk": data_other.pk}
            ),
            data
        )

        self.assertEqual(result.status_code, 200)
        data_other = DataOther.objects.get(pk=data_other.id)
        self.assertEqual(data_other.remarks_os, "edited remarks OS")
        self.assertEqual(data_other.remarks_party, "edited remarks Party")

    def test_update_immutable(self):
        submission = self.create_submission()

        data_other = DataOtherFactory(submission=submission, **REMARKS_DATA)
        submission._current_state = "finalized"
        submission.save()

        data = dict(REMARKS_DATA)
        data["remarks_os"] = "edited remarks OS"
        data["remarks_party"] = "edited remarks Party"

        result = self.client.put(
            reverse(
                "core:submission-data-others-detail",
                kwargs={"submission_pk": submission.pk, "pk": data_other.pk}
            ),
            data
        )

        self.assertEqual(result.status_code, 422)

    def test_clone(self):
        submission = self.create_submission()

        data_other = DataOtherFactory(submission=submission, **REMARKS_DATA)
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
        new_data_other = Submission.objects.get(pk=new_id).dataothers.first()
        self.assertEqual({
            'remarks_os': new_data_other.remarks_os,
            'remarks_party': new_data_other.remarks_party,
        }, REMARKS_DATA)
