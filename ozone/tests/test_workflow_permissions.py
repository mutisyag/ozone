from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import Argon2PasswordHasher

from .factories import (
    PartyFactory,
    RegionFactory,
    ReporterUserFactory,
    SecretariatUserFactory,
    SubmissionFactory,
    SubregionFactory,
)


User = get_user_model()


class BaseWorkflowPermissionsTests(TestCase):

    def setUp(self):
        super().setUp()
        self.workflow_class = 'base'
        self.hash_alg = Argon2PasswordHasher()
        self.secretariat_user = SecretariatUserFactory(
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        self.reporter = ReporterUserFactory(
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        self.region = RegionFactory.create()
        self.subregion = SubregionFactory.create(region=self.region)

    def get_authorization_header(self, username, password):
        resp = self.client.post(reverse("core:auth-token-list"), {
            "username": username,
            "password": password,
        }, format="json")
        return {
            'HTTP_AUTHORIZATION': 'Token ' + resp.data['token'],
        }

    def call_transition(
            self,
            owner,
            user,
            party,
            current_state,
            transition,
            previous_state=None,
            flag_valid=None
    ):
        submission = SubmissionFactory(
            party=party,
            created_by=owner,
            last_edited_by=owner,
        )
        # To proper instantiate the workflow class, we need a second call to save method.
        # Also here we change the current state.
        submission._workflow_class = self.workflow_class
        submission._previous_state = previous_state
        submission._current_state = current_state
        submission.flag_valid = flag_valid
        submission.save()

        headers = self.get_authorization_header(user.username, 'qwe123qwe')
        return self.client.post(
            reverse("core:submission-call-transition",
                    kwargs={'pk': submission.pk}),
            {"transition": transition, "party": party.pk},
            **headers
        )


class DefaultWorkflowPermissionsTests(BaseWorkflowPermissionsTests):

    def setUp(self):
        super().setUp()
        self.workflow_class = 'default'

    def test_submit_secretariat_owner(self):
        """
        Testing `submit` transition using a secretariat user for a submission
        created by the same secretariat user.
        Expected result: 200.
        """

        party = PartyFactory(subregion=self.subregion)
        resp = self.call_transition(
            owner=self.secretariat_user,
            user=self.secretariat_user,
            party=party,
            current_state='data_entry',
            transition='submit'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'submitted')

    def test_submit_secretariat_not_owner(self):
        """
        Testing `submit` transition using a secretariat user for a submission
        created by a party reporter.
        Expected result: 412 Precondition Failed - the user is a secretariat
        member but he is not the owner of the submission.
        """

        party = PartyFactory(subregion=self.subregion)
        self.reporter.party = party
        self.reporter.save()
        resp = self.call_transition(
            owner=self.reporter,
            user=self.secretariat_user,
            party=party,
            current_state='data_entry',
            transition='submit'
        )
        self.assertEqual(resp.status_code, 412)

    def test_submit_same_party(self):
        """
        Testing `submit` transition using a party reporter user for a submission
        created by another user from the same party.
        Expected result: 200.
        """

        party = PartyFactory(subregion=self.subregion)
        self.reporter.party = party
        self.reporter.save()
        reporter_same_party = ReporterUserFactory(
            party=party,
            username='reporter_same_party',
            email='reporter_same_party@example.com',
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        resp = self.call_transition(
            owner=self.reporter,
            user=reporter_same_party,
            party=party,
            current_state='data_entry',
            transition='submit',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'submitted')

    def test_submit_another_party(self):
        """
        Testing `submit` transition using a party reporter user for a submission
        created by another user from another party.
        Expected result: 403 Forbidden.
        """

        party = PartyFactory(subregion=self.subregion)
        self.reporter.party = party
        self.reporter.save()
        another_party = PartyFactory(
            abbr='AP',
            name='Another Party',
            subregion=self.subregion
        )
        reporter_another_party = ReporterUserFactory(
            party=another_party,
            username='reporter_another_party',
            email='reporter_another_party@example.com',
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        resp = self.call_transition(
            owner=self.reporter,
            user=reporter_another_party,
            party=party,
            current_state='data_entry',
            transition='submit'
        )
        self.assertEqual(resp.status_code, 403)

    def test_process_non_ro_secretariat(self):
        """
        Testing `process` transition using a secretariat user with write permissions.
        Expected result: 200.
        """

        party = PartyFactory(subregion=self.subregion)
        resp = self.call_transition(
            owner=self.secretariat_user,
            user=self.secretariat_user,
            party=party,
            current_state='submitted',
            transition='process'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'processing')

    def test_process_ro_secretariat(self):
        """
        Testing `process` transition using a secretariat user with read only
        permissions.
        Expected result: 403 Forbidden.
        """

        party = PartyFactory(subregion=self.subregion)
        secretariat_user_ro = SecretariatUserFactory(
            username='secretariat_user_ro',
            email='secretariat_user_ro@example.com',
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123'),
            is_read_only=True
        )
        resp = self.call_transition(
            owner=self.secretariat_user,
            user=secretariat_user_ro,
            party=party,
            current_state='submitted',
            transition='process'
        )
        self.assertEqual(resp.status_code, 403)

    def test_recall_secretariat_owner(self):
        """
        Testing `recall` transition using a secretariat user for a submission
        created by the same secretariat user.
        Expected result: 200.

        Note: For all the tests related to `recall` transition, we will recall
        a submission from the `submitted` state.
        """

        party = PartyFactory(subregion=self.subregion)
        resp = self.call_transition(
            owner=self.secretariat_user,
            user=self.secretariat_user,
            party=party,
            current_state='submitted',
            transition='recall'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'recalled')

    def test_recall_secretariat_not_owner(self):
        """
        Testing `recall` transition using a secretariat user for a submission
        created by a party reported.
        Expected result: 412.
        """

        party = PartyFactory(subregion=self.subregion)
        self.reporter.party = party
        self.reporter.save()
        resp = self.call_transition(
            owner=self.reporter,
            user=self.secretariat_user,
            party=party,
            current_state='submitted',
            transition='recall'
        )
        self.assertEqual(resp.status_code, 412)

    def test_recall_same_party(self):
        """
        Testing `recall` transition using a party reporter user for a submission
        created by another user from the same party.
        Expected result: 200.
        """

        party = PartyFactory(subregion=self.subregion)
        self.reporter.party = party
        self.reporter.save()
        reporter_same_party = ReporterUserFactory(
            party=party,
            username='reporter_same_party',
            email='reporter_same_party@example.com',
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        resp = self.call_transition(
            owner=self.reporter,
            user=reporter_same_party,
            party=party,
            current_state='submitted',
            transition='recall',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'recalled')

    def test_recall_another_party(self):
        """
        Testing `recall` transition using a party reporter user for a submission
        created by another user from the same party.
        Expected result: 403 Forbidden.
        """

        party = PartyFactory(subregion=self.subregion)
        self.reporter.party = party
        self.reporter.save()
        another_party = PartyFactory(
            abbr='AP',
            name='Another Party',
            subregion=self.subregion
        )
        reporter_another_party = ReporterUserFactory(
            party=another_party,
            username='reporter_another_party',
            email='reporter_another_party@example.com',
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        resp = self.call_transition(
            owner=self.reporter,
            user=reporter_another_party,
            party=party,
            current_state='submitted',
            transition='recall',
        )
        self.assertEqual(resp.status_code, 403)

    def test_unrecall_secretariat_owner(self):
        """
        Testing `unrecall_to_submitted` using a secretariat user for a submission
        created by the same secretariat user.
        Expected result: 200.

        Note: For all the tests related to `unrecall` transition, we will use
        `unrecall_to_submitted` transition because the tests for `unrecall_to_processing`
        and `unrecall_to_finalized` will be almost identical.
        """

        party = PartyFactory(subregion=self.subregion)
        resp = self.call_transition(
            owner=self.secretariat_user,
            user=self.secretariat_user,
            party=party,
            current_state='recalled',
            transition='unrecall_to_submitted',
            previous_state='submitted'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'submitted')

    def test_unrecall_secretariat_not_owner(self):
        """
        Testing `unrecall_to_submitted` using a secretariat user for a submission
        created by a party reporter.
        Expected result: 412 Precondition Failed.
        """

        party = PartyFactory(subregion=self.subregion)
        self.reporter.party = party
        self.reporter.save()
        resp = self.call_transition(
            owner=self.reporter,
            user=self.secretariat_user,
            party=party,
            current_state='recalled',
            transition='unrecall_to_submitted',
            previous_state='submitted'
        )
        self.assertEqual(resp.status_code, 412)

    def test_unrecall_same_party(self):
        """
        Testing `unrecall_to_submitted` transition using a party reporter user
        for a submission created by another user from the same party.
        Expected result: 200.
        """

        party = PartyFactory(subregion=self.subregion)
        self.reporter.party = party
        self.reporter.save()
        reporter_same_party = ReporterUserFactory(
            party=party,
            username='reporter_same_party',
            email='reporter_same_party@example.com',
            password=self.hash_alg.encode(password='qwe123qwe',
                                          salt='123salt123')
        )
        resp = self.call_transition(
            owner=self.reporter,
            user=reporter_same_party,
            party=party,
            current_state='recalled',
            transition='unrecall_to_submitted',
            previous_state='submitted'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'submitted')

    def test_unrecall_another_party(self):
        """
        Testing `unrecall_to_submitted` transition using a party reporter user
        for a submission created by another user from another party.
        Expected result: 403 Forbidden.
        """

        party = PartyFactory(subregion=self.subregion)
        self.reporter.party = party
        self.reporter.save()
        another_party = PartyFactory(
            abbr='AP',
            name='Another Party',
            subregion=self.subregion
        )
        reporter_another_party = ReporterUserFactory(
            party=another_party,
            username='reporter_another_party',
            email='reporter_another_party@example.com',
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        resp = self.call_transition(
            owner=self.reporter,
            user=reporter_another_party,
            party=party,
            current_state='recalled',
            transition='unrecall_to_submitted',
            previous_state='submitted'
        )
        self.assertEqual(resp.status_code, 403)

    def test_finalize_non_ro_secretariat(self):
        """
        Testing `process` transition using a secretariat user with write permissions.
        Expected result: 200.
        """

        party = PartyFactory(subregion=self.subregion)
        resp = self.call_transition(
            owner=self.secretariat_user,
            user=self.secretariat_user,
            party=party,
            current_state='processing',
            transition='finalize',
            flag_valid=True
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'finalized')

    def test_finalize_ro_secretariat(self):
        """
        Testing `process` transition using a secretariat user with read only
        permissions.
        Expected result: 403 Forbidden.
        """

        party = PartyFactory(subregion=self.subregion)
        secretariat_user_ro = SecretariatUserFactory(
            username='secretariat_user_ro',
            email='secretariat_user_ro@example.com',
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123'),
            is_read_only=True
        )
        resp = self.call_transition(
            owner=self.secretariat_user,
            user=secretariat_user_ro,
            party=party,
            current_state='processing',
            transition='finalize',
            flag_valid=True
        )
        self.assertEqual(resp.status_code, 403)


class AcceleratedWorkflowTests(BaseWorkflowPermissionsTests):

    def setUp(self):
        super().setUp()
        self.workflow_class = 'accelerated'

    def test_finalize_non_ro_secretariat(self):
        """
        Testing `finalize` transition using a secretariat user with write permissions.
        Expected result: 200.
        """

        party = PartyFactory(subregion=self.subregion)
        resp = self.call_transition(
            owner=self.secretariat_user,
            user=self.secretariat_user,
            party=party,
            current_state='data_entry',
            transition='finalize'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'finalized')

    def test_finalize_ro_secretariat(self):
        """
        Testing `finalize` transition using a secretariat user with read only
        permissions.
        Expected result: 403 Forbidden.
        """

        party = PartyFactory(subregion=self.subregion)
        secretariat_user_ro = SecretariatUserFactory(
            username='secretariat_user_ro',
            email='secretariat_user_ro@example.com',
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123'),
            is_read_only=True
        )
        resp = self.call_transition(
            owner=self.secretariat_user,
            user=secretariat_user_ro,
            party=party,
            current_state='data_entry',
            transition='finalized'
        )
        self.assertEqual(resp.status_code, 403)

    def test_recall_non_ro_secretariat(self):
        """
        Testing `recall` transition using a secretariat user with write permissions.
        Expected result: 200.
        """

        party = PartyFactory(subregion=self.subregion)
        resp = self.call_transition(
            owner=self.secretariat_user,
            user=self.secretariat_user,
            party=party,
            current_state='finalized',
            transition='recall'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'recalled')

    def test_recall_ro_secretariat(self):
        """
        Testing `recall` transition using a secretariat user with read only
        permissions.
        Expected result: 403 Forbidden.
        """

        party = PartyFactory(subregion=self.subregion)
        secretariat_user_ro = SecretariatUserFactory(
            username='secretariat_user_ro',
            email='secretariat_user_ro@example.com',
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123'),
            is_read_only=True
        )
        resp = self.call_transition(
            owner=self.secretariat_user,
            user=secretariat_user_ro,
            party=party,
            current_state='finalized',
            transition='recall'
        )
        self.assertEqual(resp.status_code, 403)

    def test_unrecall_non_ro_secretariat(self):
        """
        Testing `unrecall` transition using a secretariat user with write permissions.
        Expected result: 200.
        """

        party = PartyFactory(subregion=self.subregion)
        resp = self.call_transition(
            owner=self.secretariat_user,
            user=self.secretariat_user,
            party=party,
            current_state='recalled',
            transition='unrecall'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'finalized')

    def test_unrecall_ro_secretariat(self):
        """
        Testing `unrecall` transition using a secretariat user with read only
        permissions.
        Expected result: 403 Forbidden.
        """

        party = PartyFactory(subregion=self.subregion)
        secretariat_user_ro = SecretariatUserFactory(
            username='secretariat_user_ro',
            email='secretariat_user_ro@example.com',
            password=self.hash_alg.encode(password='qwe123qwe', salt='123salt123'),
            is_read_only=True
        )
        resp = self.call_transition(
            owner=self.secretariat_user,
            user=secretariat_user_ro,
            party=party,
            current_state='recalled',
            transition='unrecall'
        )
        self.assertEqual(resp.status_code, 403)
