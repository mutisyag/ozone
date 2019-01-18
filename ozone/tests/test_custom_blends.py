from django.urls import reverse
from django.contrib.auth.hashers import Argon2PasswordHasher

from ozone.core.models import Blend

from .base import BaseTests
from .factories import (
    PartyFactory,
    RegionFactory,
    ReporterUserFactory,
    ReportingChannelFactory,
    SecretariatUserFactory,
    SubmissionFactory,
    SubregionFactory,
    SubstanceFactory,
    AnotherSubstanceFactory,
    AnotherPartyFactory,
    BlendFactory,
)


class BaseCustomBlendsTests(BaseTests):
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
        self.substance1 = SubstanceFactory()
        self.substance2 = AnotherSubstanceFactory()
        ReportingChannelFactory()

    def create_submission(self, **kwargs):
        submission = SubmissionFactory.create(
            party=self.party,
            created_by=self.secretariat_user,
            last_edited_by=self.secretariat_user,
            **kwargs,
        )
        return submission

    def blend_data(self, party):
        return {
            "components": [
                {
                    "component_name": "",
                    "substance": self.substance1.id,
                    "percentage": 0.4,
                },
                {
                    "component_name": "",
                    "substance": self.substance2.id,
                    "percentage": 0.6,
                },
            ],
            "blend_id": "Testing",
            "type": "Custom",
            "party": party.pk,
        }


class CustomBlendTests(BaseCustomBlendsTests):
    def test_create_custom_blend_as_party(self):
        self.client.login(username=self.party_user.username, password='qwe123qwe')
        resp = self.client.post(
            reverse("core:blends-list"),
            self.blend_data(self.party),
        )
        self.assertEqual(resp.status_code, 201)

        new_blend = Blend.objects.get(pk=resp.json()["id"])
        self.assertEqual(new_blend.party, self.party)

        components = new_blend.components.order_by("substance_id").all()
        self.assertEqual(components[0].substance, self.substance1)
        self.assertEqual(components[1].substance, self.substance2)

    def test_create_custom_blend_as_party_for_another_party(self):
        self.client.login(username=self.party_user.username, password='qwe123qwe')
        resp = self.client.post(
            reverse("core:blends-list"),
            self.blend_data(self.another_party),
        )
        self.assertEqual(resp.status_code, 403)

    def test_create_custom_blend_as_secretariat(self):
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.client.post(
            reverse("core:blends-list"),
            self.blend_data(self.party),
        )
        self.assertEqual(resp.status_code, 201)

        new_blend = Blend.objects.get(pk=resp.json()["id"])
        self.assertEqual(new_blend.party, self.party)

        components = new_blend.components.order_by("substance_id").all()
        self.assertEqual(components[0].substance, self.substance1)
        self.assertEqual(components[1].substance, self.substance2)

    def test_list_custom_blends_as_secretariat_same_party(self):
        blend = BlendFactory.create(party=self.party)
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.client.get(
            reverse("core:blends-list"),
            {"party": self.party.id},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(resp.json()[0]["id"], blend.id)

    def test_list_custom_blends_as_secretariat_different_party(self):
        blend = BlendFactory.create(party=self.another_party)
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.client.get(
            reverse("core:blends-list"),
            {"party": self.party.id},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 0)

    def test_list_custom_blends_as_party_same_party(self):
        blend = BlendFactory.create(party=self.party)
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.client.get(
            reverse("core:blends-list"),
            {"party": self.party.id},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(resp.json()[0]["id"], blend.id)

    def test_list_custom_blends_as_party_different_party(self):
        blend = BlendFactory.create(party=self.another_party)
        self.client.login(username=self.party_user.username, password='qwe123qwe')
        resp = self.client.get(
            reverse("core:blends-list"),
            {"party": self.party.id},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 0)

    def test_list_custom_blends_as_party_same_party_no_param(self):
        blend = BlendFactory.create(party=self.party)
        self.client.login(username=self.party_user.username, password='qwe123qwe')
        resp = self.client.get(
            reverse("core:blends-list"),
            {},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(resp.json()[0]["id"], blend.id)

    def test_list_custom_blends_as_party_different_party_no_param(self):
        blend = BlendFactory.create(party=self.another_party)
        self.client.login(username=self.party_user.username, password='qwe123qwe')
        resp = self.client.get(
            reverse("core:blends-list"),
            {},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 0)

    def test_add_data_with_custom_blend_same_party(self):
        blend = BlendFactory.create(party=self.party)
        self.client.login(username=self.party_user.username, password='qwe123qwe')
        submission = self.create_submission()

        data = {"blend": blend.id, "quantity_total_new": 1}
        resp = self.client.post(
            reverse(
                "core:submission-article7-imports-list",
                kwargs={"submission_pk": submission.pk},
            ),
            [data],
        )
        self.assertEqual(resp.status_code, 201)

    def test_add_data_with_custom_blend_different_party(self):
        blend = BlendFactory.create(party=self.another_party)
        self.client.login(username=self.party_user.username, password='qwe123qwe')
        submission = self.create_submission()

        data = {"blend": blend.id, "quantity_total_new": 1}
        resp = self.client.post(
            reverse(
                "core:submission-article7-imports-list",
                kwargs={"submission_pk": submission.pk},
            ),
            [data],
        )
        self.assertEqual(resp.status_code, 422)
