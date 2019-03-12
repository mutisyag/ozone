from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import Argon2PasswordHasher

from ozone.core.models import Article7Emission, Blend, Submission

from .base import BaseTests
from .factories import (
    AnotherPartyFactory,
    BlendFactory,
    ObligationFactory,
    PartyFactory,
    ReporterUserFactory,
    ReporterUserROFactory,
    ReporterUserSamePartyFactory,
    ReporterUserAnotherPartyFactory,
    ReportingPeriodFactory,
    SecretariatUserFactory,
    SecretariatUserROFactory,
    SubmissionFactory,
    SubregionFactory,
    RegionFactory,
    ReportingChannelFactory
)

User = get_user_model()


class BaseUserRoleTests(BaseTests):
    _form_type = "art7"

    def setUp(self):
        super().setUp()
        self.hash_alg = Argon2PasswordHasher()
        self.region = RegionFactory.create()
        self.subregion = SubregionFactory.create(region=self.region)
        self.party = PartyFactory.create(subregion=self.subregion)
        self.obligation = ObligationFactory.create(_form_type=self._form_type)
        ReportingChannelFactory()


class TestSecretariatEditRole(BaseUserRoleTests):

    def setUp(self):
        super().setUp()
        self.secretariat_user = SecretariatUserFactory(
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')

    def test_create_submission(self):
        """
        Test creating submission on behalf of a party.
        """

        period = ReportingPeriodFactory()
        data = {
            "party": self.party.id,
            "reporting_period": period.id,
            "obligation": self.obligation.id,
        }
        resp = self.client.post(
            reverse("core:submission-list"),
            data
        )
        self.assertEqual(resp.status_code, 201)

        submission = Submission.objects.get(id=resp.data["id"])
        self.assertEqual(submission.party, self.party)
        self.assertEqual(submission.obligation, self.obligation)
        self.assertEqual(submission.reporting_period, period)

    def test_view_submission(self):
        """
        Test viewing submission on behalf of a party.
        """

        submission = SubmissionFactory(
            party=self.party,
            obligation=self.obligation,
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
        Test editing submission on behalf of a party.
        """

        submission = SubmissionFactory(
            party=self.party,
            obligation=self.obligation,
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
        Test deleting submission on behalf of a party.
        """

        submission = SubmissionFactory(
            party=self.party,
            obligation=self.obligation,
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
        Test creating blend on behalf of a party.
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
        Test editing blend on behalf of a party.
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
        Test deleting blend on behalf of a party.
        """

        blend = BlendFactory(party=self.party)
        self.assertEqual(Blend.objects.count(), 1)
        resp = self.client.delete(
            reverse("core:blends-detail", kwargs={'pk': blend.pk})
        )
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(Blend.objects.count(), 0)


class TestSecretariatReadOnlyRole(BaseUserRoleTests):

    def setUp(self):
        super().setUp()
        self.secretariat_user_ro = SecretariatUserROFactory(
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        self.client.login(username=self.secretariat_user_ro.username, password='qwe123qwe')

    def test_create_submission(self):
        """
        Test creating submission on behalf of a party.
        """

        period = ReportingPeriodFactory()
        data = {
            "party": self.party.id,
            "reporting_period": period.id,
            "obligation": self.obligation.id,
        }
        resp = self.client.post(
            reverse("core:submission-list"),
            data
        )
        self.assertEqual(resp.status_code, 403)

    def test_view_submission(self):
        """
        Test viewing submission on behalf of a party.
        """

        submission = SubmissionFactory(
            party=self.party,
            obligation=self.obligation,
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
        Test editing submission on behalf of a party.
        """

        submission = SubmissionFactory(
            party=self.party,
            obligation=self.obligation,
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
        Test deleting submission on behalf of a party.
        """

        submission = SubmissionFactory(
            party=self.party,
            obligation=self.obligation,
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
        Test creating blend on behalf of a party.
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
        Test editing blend on behalf of a party.
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
        Test deleting blend on behalf of a party.
        """

        blend = BlendFactory(party=self.party)
        self.assertEqual(Blend.objects.count(), 1)
        resp = self.client.delete(
            reverse("core:blends-detail", kwargs={'pk': blend.pk}),
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Blend.objects.count(), 1)


class TestPartyReporterRole(BaseUserRoleTests):

    def setUp(self):
        super().setUp()
        self.another_party = AnotherPartyFactory(subregion=self.subregion)

        self.reporter = ReporterUserFactory(
            party=self.party,
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        self.reporter_same_party = ReporterUserSamePartyFactory(
            party=self.party,
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        self.reporter_another_party = ReporterUserAnotherPartyFactory(
            party=self.another_party,
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        self.client.login(username=self.reporter.username, password='qwe123qwe')

    def test_view_submission_same_party(self):
        """
        Test viewing submission reported by my party.
        """
        submission = SubmissionFactory(
            party=self.party,
            obligation=self.obligation,
            created_by=self.reporter_same_party,
            last_edited_by=self.reporter_same_party,
        )
        resp = self.client.get(
            reverse("core:submission-detail", kwargs={"pk": submission.id})
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["id"], submission.id)

    def test_view_submission_another_party(self):
        """
        Test viewing submission reported by another party.
        """
        submission = SubmissionFactory(
            party=self.another_party,
            obligation=self.obligation,
            created_by=self.reporter_another_party,
            last_edited_by=self.reporter_another_party,
        )
        resp = self.client.get(
            reverse("core:submission-detail", kwargs={"pk": submission.id})
        )
        self.assertEqual(resp.status_code, 404)

    def test_edit_submission_same_party(self):
        """
        Test editing submission reported by my party.
        """

        submission = SubmissionFactory(
            party=self.party,
            obligation=self.obligation,
            created_by=self.reporter_same_party,
            last_edited_by=self.reporter_same_party,
        )
        data = {
            "id": 1,
            "remarks_party": "Test",
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

    def test_edit_submission_another_party(self):
        """
        Test editing submission reported by another party.
        """

        submission = SubmissionFactory(
            party=self.another_party,
            obligation=self.obligation,
            created_by=self.reporter_another_party,
            last_edited_by=self.reporter_another_party,
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

    def test_delete_submission_same_party(self):
        """
        Test deleting submission reported by my party.
        """

        submission = SubmissionFactory(
            party=self.party,
            obligation=self.obligation,
            created_by=self.reporter_same_party,
            last_edited_by=self.reporter_same_party,
        )
        self.assertEqual(Submission.objects.count(), 1)
        resp = self.client.delete(
            reverse("core:submission-detail", kwargs={'pk': submission.pk}),
            {"party": submission.party.pk}
        )
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(Submission.objects.count(), 0)

    def test_delete_submission_another_party(self):
        """
        Test deleting submission reported by another party.
        """

        submission = SubmissionFactory(
            party=self.another_party,
            obligation=self.obligation,
            created_by=self.reporter_another_party,
            last_edited_by=self.reporter_another_party,
        )
        self.assertEqual(Submission.objects.count(), 1)
        resp = self.client.delete(
            reverse("core:submission-detail", kwargs={'pk': submission.pk}),
            {"party": submission.party.pk}
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Submission.objects.count(), 1)

    def test_edit_blend_same_party(self):
        """
        Test editing blend on behalf of my party.
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

    def test_edit_blend_another_party(self):
        """
        Test editing blend on behalf of another party.
        """

        blend = BlendFactory(party=self.another_party)
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

    def test_delete_blend_same_party(self):
        """
        Test deleting blend on behalf of my party.
        """

        blend = BlendFactory(party=self.party)
        self.assertEqual(Blend.objects.count(), 1)
        resp = self.client.delete(
            reverse("core:blends-detail", kwargs={'pk': blend.pk})
        )
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(Blend.objects.count(), 0)

    def test_delete_blend_another_party(self):
        """
        Test deleting blend on behalf of another party.
        """

        blend = BlendFactory(party=self.another_party)
        resp = self.client.delete(
            reverse("core:blends-detail", kwargs={'pk': blend.pk})
        )
        self.assertEqual(resp.status_code, 403)


class TestPartyReporterReadOnlyRole(BaseUserRoleTests):

    def setUp(self):
        super().setUp()
        self.another_party = AnotherPartyFactory(subregion=self.subregion)

        self.reporter_ro = ReporterUserROFactory(
            party=self.party,
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        self.reporter_same_party = ReporterUserSamePartyFactory(
            party=self.party,
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        self.reporter_another_party = ReporterUserAnotherPartyFactory(
            party=self.another_party,
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        self.client.login(username=self.reporter_ro.username, password='qwe123qwe')

    def test_view_submission_same_party(self):
        """
        Test viewing submission reported by my party.
        """
        submission = SubmissionFactory(
            party=self.party,
            obligation=self.obligation,
            created_by=self.reporter_same_party,
            last_edited_by=self.reporter_same_party,
        )
        resp = self.client.get(
            reverse("core:submission-detail", kwargs={"pk": submission.id})
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["id"], submission.id)

    def test_view_submission_another_party(self):
        """
        Test viewing submission reported by another party.
        """
        submission = SubmissionFactory(
            party=self.another_party,
            obligation=self.obligation,
            created_by=self.reporter_another_party,
            last_edited_by=self.reporter_another_party,
        )
        resp = self.client.get(
            reverse("core:submission-detail", kwargs={"pk": submission.id})
        )
        self.assertEqual(resp.status_code, 404)

    def test_create_submission(self):
        """
        Test creating submission.
        """

        period = ReportingPeriodFactory()
        data = {
            "party": self.party.id,
            "reporting_period": period.id,
            "obligation": self.obligation.id,
        }
        resp = self.client.post(
            reverse("core:submission-list"),
            data
        )
        self.assertEqual(resp.status_code, 403)

    def test_edit_submission_same_party(self):
        """
        Test editing submission reported by my party.
        """

        submission = SubmissionFactory(
            party=self.party,
            obligation=self.obligation,
            created_by=self.reporter_same_party,
            last_edited_by=self.reporter_same_party,
        )
        data = {
            "id": 1,
            "remarks_party": "Test",
            "remarks_os": "Test",
            "ordering_id": 0,
            "facility_name": "Test",
            "quantity_emitted": 1,
        }
        resp = self.client.post(
            reverse("core:submission-article7-emissions-list",
                    kwargs={'submission_pk': submission.pk}),
            data
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Article7Emission.objects.count(), 0)

    def test_delete_submission_same_party(self):
        """
        Test deleting submission reported by my party.
        """

        submission = SubmissionFactory(
            party=self.party,
            obligation=self.obligation,
            created_by=self.reporter_same_party,
            last_edited_by=self.reporter_same_party,
        )
        self.assertEqual(Submission.objects.count(), 1)
        resp = self.client.delete(
            reverse("core:submission-detail", kwargs={'pk': submission.pk}),
            {"party": submission.party.pk}
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Submission.objects.count(), 1)

    def test_create_blend_same_party(self):
        """
        Test creating blend on behalf of a party.
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

    def test_edit_blend_same_party(self):
        """
        Test editing blend on behalf of my party.
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

    def test_delete_blend_same_party(self):
        """
        Test deleting blend on behalf of my party.
        """

        blend = BlendFactory(party=self.party)
        resp = self.client.delete(
            reverse("core:blends-detail", kwargs={'pk': blend.pk})
        )
        self.assertEqual(resp.status_code, 403)


class TestPublicUserRole(BaseUserRoleTests):

    def setUp(self):
        super().setUp()
        self.reporter = ReporterUserFactory(
            party=self.party,
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )

    def test_view_submission_same_party(self):
        """
        Test viewing submission using a public user.
        """

        submission = SubmissionFactory(
            party=self.party,
            obligation=self.obligation,
            created_by=self.reporter,
            last_edited_by=self.reporter,
        )

        resp = self.client.get(
            reverse("core:submission-detail", kwargs={"pk": submission.id})
        )
        self.assertEqual(resp.status_code, 401)

    def test_create_submission(self):
        """
        Test creating submission using a public user.
        """

        period = ReportingPeriodFactory()
        data = {
            "party": self.party.id,
            "reporting_period": period.id,
            "obligation": self.obligation.id,
        }
        resp = self.client.post(
            reverse("core:submission-list"),
            data
        )
        self.assertEqual(resp.status_code, 401)

    def test_edit_submission(self):
        """
        Test editing submission using a public user.
        """

        submission = SubmissionFactory(
            party=self.party,
            obligation=self.obligation,
            created_by=self.reporter,
            last_edited_by=self.reporter,
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
        self.assertEqual(resp.status_code, 401)

    def test_delete_submission(self):
        """
        Test deleting submission for a party.
        """

        submission = SubmissionFactory(
            party=self.party,
            obligation=self.obligation,
            created_by=self.reporter,
            last_edited_by=self.reporter,
        )
        self.assertEqual(Submission.objects.count(), 1)
        resp = self.client.delete(
            reverse("core:submission-detail", kwargs={'pk': submission.pk})
        )
        self.assertEqual(resp.status_code, 401)

    def test_create_blend(self):
        """
        Test creating blend on behalf of a party.
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
        self.assertEqual(resp.status_code, 401)

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
        self.assertEqual(resp.status_code, 401)

    def test_delete_blend(self):
        """
        Test deleting blend.
        """

        blend = BlendFactory(party=self.party)
        resp = self.client.delete(
            reverse("core:blends-detail", kwargs={'pk': blend.pk})
        )
        self.assertEqual(resp.status_code, 401)
