from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import Argon2PasswordHasher

from ozone.core.models import Article7Emission, Blend, Submission

from .base import BaseTests
from .factories import (
    BlendFactory,
    ObligationFactory,
    PartyFactory,
    ReportingPeriodFactory,
    SecretariatUserFactory,
    SecretariatUserROFactory,
    SubmissionFactory,
    SubregionFactory,
    RegionFactory,
)

User = get_user_model()


class BaseUserRoleTests(BaseTests):

    def setUp(self):
        super().setUp()
        self.hash_alg = Argon2PasswordHasher()
        self.region = RegionFactory.create()
        self.subregion = SubregionFactory.create(region=self.region)
        self.party = PartyFactory.create(subregion=self.subregion)


class TestSecretariatEditRole(BaseUserRoleTests):

    def setUp(self):
        super().setUp()
        self.secretariat_user = SecretariatUserFactory(
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.get_token(
                username=self.secretariat_user.username,
                password='qwe123qwe'
            )
        )

    def test_create_submission(self):
        """
        Test creating submission for party.
        """

        period = ReportingPeriodFactory()
        obligation = ObligationFactory()
        data = {
            "party": self.party.id,
            "reporting_period": period.id,
            "obligation": obligation.id,
        }
        resp = self.client.post(
            reverse("core:submission-list"),
            data
        )
        self.assertEqual(resp.status_code, 201)

        submission = Submission.objects.get(id=resp.data["id"])
        self.assertEqual(submission.party, self.party)
        self.assertEqual(submission.obligation, obligation)
        self.assertEqual(submission.reporting_period, period)

    def test_view_submission(self):
        """
        Test viewing submission for party.
        """

        submission = SubmissionFactory(
            party=self.party,
            created_by=self.secretariat_user,
            last_edited_by=self.secretariat_user,
        )

        resp = self.client.get(
            reverse("core:submission-detail", kwargs={"pk": submission.id})
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["id"], submission.id)

    def test_edit_submission(self):
        """
        Test editing submission for a party.
        """

        submission = SubmissionFactory(
            party=self.party,
            created_by=self.secretariat_user,
            last_edited_by=self.secretariat_user,
        )
        data = {
            "id": 1,
            "remarks_party": "Test",
            "remarks_os": "Test",
            "ordering_id": 0,
            "facility_name": "Test",
            "quantity_emitted": 1
        }
        resp = self.client.post(
            reverse("core:submission-article7-emissions-list",
                    kwargs={'submission_pk': submission.pk}),
            data
        )
        self.assertEqual(resp.status_code, 201)
        emission = Article7Emission.objects.get(id=resp.data["id"])
        self.assertEqual(emission.facility_name, 'Test')
        self.assertEqual(emission.quantity_emitted, 1)

    def test_delete_submission(self):
        """
        Test deleting submission for a party.
        """

        submission = SubmissionFactory(
            party=self.party,
            created_by=self.secretariat_user,
            last_edited_by=self.secretariat_user,
        )
        self.assertEqual(Submission.objects.count(), 1)
        resp = self.client.delete(
            reverse("core:submission-detail", kwargs={'pk': submission.pk})
        )
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(Submission.objects.count(), 0)

    def test_create_blend(self):
        """
        Test creating blend.
        """

        data = {
            "blend_id": "TEST",
            "party": self.party.id,
            "type": "Zeotrope",
            "composition": "TEST",
            "components": []
        }

        self.assertEqual(Blend.objects.count(), 0)
        resp = self.client.post(
            reverse("core:blends-list"),
            data
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Blend.objects.count(), 1)
        self.assertEqual(Blend.objects.get(pk=resp.data['id']).blend_id, data['blend_id'])

    def test_edit_blend(self):
        """
        Test editing blend.
        """

        blend = BlendFactory(party=self.party)
        data = {
            "blend_id": "TEST",
            "type": "Azeotrope",
            "components": []
        }
        resp = self.client.put(
            reverse("core:blends-detail", kwargs={'pk': blend.pk}),
            data
        )
        self.assertEqual(blend.blend_id, 'TB')
        self.assertEqual(blend.type, 'Zeotrope')
        self.assertEqual(resp.status_code, 200)
        blend = Blend.objects.get(pk=resp.data['id'])
        self.assertEqual(blend.blend_id, 'TEST')
        self.assertEqual(blend.type, 'Azeotrope')

    def test_delete_blend(self):
        """
        Test deleting blend.
        """

        blend = BlendFactory(party=self.party)
        self.assertEqual(Blend.objects.count(), 1)
        resp = self.client.delete(
            reverse("core:blends-detail", kwargs={'pk': blend.pk})
        )
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(Blend.objects.count(), 0)

    def test_access_admin(self):
        """
        Test accessing admin area.
        """

        resp = self.client.get('/admin/')
        self.assertEqual(resp.status_code, 302)


class TestSecretariatReadOnlyRole(BaseUserRoleTests):

    def setUp(self):
        super().setUp()
        self.secretariat_user_ro = SecretariatUserROFactory(
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.get_token(
                username=self.secretariat_user_ro.username,
                password='qwe123qwe'
            )
        )

    def test_create_submission(self):
        """
        Test creating submission for party.
        """

        period = ReportingPeriodFactory()
        obligation = ObligationFactory()
        data = {
            "party": self.party.id,
            "reporting_period": period.id,
            "obligation": obligation.id,
        }
        resp = self.client.post(
            reverse("core:submission-list"),
            data
        )
        self.assertEqual(resp.status_code, 403)

    def test_view_submission(self):
        """
        Test viewing submission for party.
        """

        submission = SubmissionFactory(
            party=self.party,
            created_by=self.secretariat_user_ro,
            last_edited_by=self.secretariat_user_ro,
        )
        resp = self.client.get(
            reverse("core:submission-detail", kwargs={"pk": submission.id})
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["id"], submission.id)

    def test_edit_submission(self):
        """
        Test editing submission for a party.
        """

        submission = SubmissionFactory(
            party=self.party,
            created_by=self.secretariat_user_ro,
            last_edited_by=self.secretariat_user_ro,
        )
        data = {
            "id": 1,
            "remarks_party": "Test",
            "remarks_os": "Test",
            "ordering_id": 0,
            "facility_name": "Test",
            "quantity_emitted": 1
        }
        resp = self.client.post(
            reverse("core:submission-article7-emissions-list",
                    kwargs={'submission_pk': submission.pk}),
            data
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Article7Emission.objects.count(), 0)

    def test_delete_submission(self):
        """
        Test deleting submission for a party.
        """

        submission = SubmissionFactory(
            party=self.party,
            created_by=self.secretariat_user_ro,
            last_edited_by=self.secretariat_user_ro,
        )
        self.assertEqual(Submission.objects.count(), 1)
        resp = self.client.delete(
            reverse("core:submission-detail", kwargs={'pk': submission.pk})
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Submission.objects.count(), 1)

    def test_create_blend(self):
        """
        Test creating blend.
        """

        data = {
            "blend_id": "TEST",
            "party": self.party.id,
            "type": "Zeotrope",
            "composition": "TEST",
            "components": []
        }

        resp = self.client.post(
            reverse("core:blends-list"),
            data
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Blend.objects.count(), 0)

    def test_edit_blend(self):
        """
        Test editing blend.
        """

        blend = BlendFactory(party=self.party)
        data = {
            "blend_id": "TEST",
            "type": "Azeotrope",
            "components": []
        }

        resp = self.client.put(
            reverse("core:blends-detail", kwargs={'pk': blend.pk}),
            data
        )
        self.assertEqual(resp.status_code, 403)

    def test_delete_blend(self):
        """
        Test deleting blend.
        """

        blend = BlendFactory(party=self.party)
        self.assertEqual(Blend.objects.count(), 1)
        resp = self.client.delete(
            reverse("core:blends-detail", kwargs={'pk': blend.pk}),
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Blend.objects.count(), 1)

    def test_access_admin(self):
        """
        Test accessing admin area.
        """

        resp = self.client.get('/admin/')
        self.assertEqual(resp.status_code, 302)
