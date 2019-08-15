from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import Argon2PasswordHasher

from .base import BaseTests
from .factories import (
    AnotherPartyFactory,
    ExemptionApprovedFactory,
    NominationFactory,
    PartyFactory,
    RegionFactory,
    LanguageEnFactory,
    ReporterUserFactory,
    ReporterUserSamePartyFactory,
    ReporterUserAnotherPartyFactory,
    ReportingChannelFactory,
    SecretariatUserFactory,
    SecretariatUserROFactory,
    SubmissionFactory,
    SubregionFactory,
    SubstanceFactory,
)


User = get_user_model()


class BaseWorkflowPermissionsTests(BaseTests):

    def setUp(self):
        super().setUp()
        self.workflow_class = 'base'

        self.region = RegionFactory.create()
        self.subregion = SubregionFactory.create(region=self.region)
        self.party = PartyFactory(subregion=self.subregion)
        self.another_party = AnotherPartyFactory(subregion=self.subregion)
        self.language = LanguageEnFactory()

        hash_alg = Argon2PasswordHasher()
        self.secretariat_user = SecretariatUserFactory(
            language=self.language,
            password=hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        self.secretariat_user_ro = SecretariatUserROFactory(
            language=self.language,
            password=hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        self.reporter = ReporterUserFactory(
            language=self.language,
            party=self.party,
            password=hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        self.reporter_same_party = ReporterUserSamePartyFactory(
            language=self.language,
            party=self.party,
            password=hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        self.reporter_another_party = ReporterUserAnotherPartyFactory(
            language=self.language,
            party=self.another_party,
            password=hash_alg.encode(password='qwe123qwe', salt='123salt123')
        )
        ReportingChannelFactory()

    def call_transition(self, submission, transition):
        return self.client.post(
            reverse("core:submission-call-transition",
                    kwargs={'pk': submission.pk}),
            {"transition": transition, "party": submission.party.pk},
        )

    def create_submission(
            self,
            owner,
            party,
            current_state,
            previous_state=None,
            flag_valid=None,
            flag_approved=None,
    ):
        submission = SubmissionFactory(
            party=party,
            created_by=owner,
            last_edited_by=owner,
        )

        # To proper instantiate the workflow class, we need a second call to
        # save method. Also here we change the current state.
        submission._workflow_class = self.workflow_class
        submission._previous_state = previous_state
        submission._current_state = current_state
        submission.flag_valid = flag_valid
        submission.flag_approved = flag_approved
        submission.save()

        return submission


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

        submission = self.create_submission(
            owner=self.secretariat_user,
            party=self.party,
            current_state='data_entry'
        )
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='submit'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'submitted')

    def test_submit_secretariat_not_owner(self):
        """
        Testing `submit` transition using a secretariat user for a submission
        created by a party reporter.
        Expected result: 412 (secretariat can call the transition endpoint (for
        other transitions), but cannot trigger this specific transition).
        """

        submission = self.create_submission(
            owner=self.reporter,
            party=self.party,
            current_state='data_entry',
        )
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='submit'
        )
        self.assertEqual(resp.status_code, 412)

    def test_submit_same_party(self):
        """
        Testing `submit` transition using a party reporter user for a submission
        created by another user from the same party.
        Expected result: 200.
        """

        submission = self.create_submission(
            owner=self.reporter,
            party=self.party,
            current_state='data_entry'
        )
        self.client.login(username=self.reporter_same_party.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='submit'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'submitted')

    def test_submit_another_party(self):
        """
        Testing `submit` transition using a party reporter user for a submission
        created by another user from another party.
        Expected result: 403 Forbidden.
        """

        submission = self.create_submission(
            owner=self.reporter,
            party=self.party,
            current_state='data_entry'
        )
        self.client.login(username=self.reporter_another_party.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='submit'
        )
        self.assertEqual(resp.status_code, 403)

    def test_process_write_secretariat(self):
        """
        Testing `process` transition using a secretariat user with write permissions.
        Expected result: 200.
        """

        submission = self.create_submission(
            owner=self.secretariat_user,
            party=self.party,
            current_state='submitted'
        )
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
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

        submission = self.create_submission(
            owner=self.secretariat_user,
            party=self.party,
            current_state='submitted',
        )
        self.client.login(username=self.secretariat_user_ro.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
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

        submission = self.create_submission(
            owner=self.secretariat_user,
            party=self.party,
            current_state='submitted',
        )
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='recall'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'recalled')

    def test_recall_secretariat_not_owner(self):
        """
        Testing `recall` transition using a secretariat user for a submission
        created by a party reporter.
        Expected result: 412 (secretariat can call the transition endpoint (for
        other transitions), but cannot trigger this specific transition).
        """

        submission = self.create_submission(
            owner=self.reporter,
            party=self.party,
            current_state='submitted'
        )
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='recall'
        )
        self.assertEqual(resp.status_code, 412)

    def test_recall_same_party(self):
        """
        Testing `recall` transition using a party reporter user for a submission
        created by another user from the same party.
        Expected result: 200.
        """

        submission = self.create_submission(
            owner=self.reporter,
            party=self.party,
            current_state='submitted'
        )
        self.client.login(username=self.reporter_same_party.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='recall'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'recalled')

    def test_recall_another_party(self):
        """
        Testing `recall` transition using a party reporter user for a submission
        created by another user from the same party.
        Expected result: 403 Forbidden.
        """

        submission = self.create_submission(
            owner=self.reporter,
            party=self.party,
            current_state='submitted'
        )
        self.client.login(username=self.reporter_another_party.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='recall',
        )
        self.assertEqual(resp.status_code, 403)

    def test_unrecall_to_submitted_secretariat_owner(self):
        """
        Testing `unrecall_to_submitted` using a secretariat user for a submission
        created by the same secretariat user.
        Expected result: 200.
        """

        submission = self.create_submission(
            owner=self.secretariat_user,
            party=self.party,
            current_state='recalled',
            previous_state='submitted'
        )
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='unrecall_to_submitted'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'submitted')

    def test_unrecall_to_processing_secretariat_owner(self):
        """
        Testing `unrecall_to_processing` using a secretariat user for a submission
        created by the same secretariat user.
        Expected result: 200.
        """

        submission = self.create_submission(
            owner=self.secretariat_user,
            party=self.party,
            current_state='recalled',
            previous_state='processing'
        )
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='unrecall_to_processing'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'processing')

    def test_unrecall_to_finalized_secretariat_owner(self):
        """
        Testing `unrecall_to_finalized` using a secretariat user for a submission
        created by the same secretariat user.
        Expected result: 200.
        """

        submission = self.create_submission(
            owner=self.secretariat_user,
            party=self.party,
            current_state='recalled',
            previous_state='finalized'
        )
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='unrecall_to_finalized'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'finalized')

    def test_unrecall_to_submitted_secretariat_not_owner(self):
        """
        Testing `unrecall_to_submitted` using a secretariat user for a
        submission created by a party reporter.
        Expected result: 412 (secretariat can call the transition endpoint (for
        other transitions), but cannot trigger this specific transition).
        """

        submission = self.create_submission(
            owner=self.reporter,
            party=self.party,
            current_state='recalled',
            previous_state='submitted'
        )
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='unrecall_to_submitted'
        )
        self.assertEqual(resp.status_code, 412)

    def test_unrecall_to_processing_secretariat_not_owner(self):
        """
        Testing `unrecall_to_processing` using a secretariat user for a
        submission created by a party reporter.
        Expected result: 412 (secretariat can call the transition endpoint (for
        other transitions), but cannot trigger this specific transition).
        """

        submission = self.create_submission(
            owner=self.reporter,
            party=self.party,
            current_state='recalled',
            previous_state='processing'
        )
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='unrecall_to_processing'
        )
        self.assertEqual(resp.status_code, 412)

    def test_unrecall_to_finalized_secretariat_not_owner(self):
        """
        Testing `unrecall_to_finalized` using a secretariat user for a submission
        created by a party reporter.
        Expected result: 412 (secretariat can call the transition endpoint (for
        other transitions), but cannot trigger this specific transition).
        """

        submission = self.create_submission(
            owner=self.reporter,
            party=self.party,
            current_state='recalled',
            previous_state='finalized'
        )
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='unrecall_to_finalized'
        )
        self.assertEqual(resp.status_code, 412)

    def test_unrecall_to_submitted_same_party(self):
        """
        Testing `unrecall_to_submitted` transition using a party reporter user
        for a submission created by another user from the same party.
        Expected result: 200.
        """

        submission = self.create_submission(
            owner=self.reporter,
            party=self.party,
            current_state='recalled',
            previous_state='submitted'
        )
        self.client.login(username=self.reporter_same_party.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='unrecall_to_submitted'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'submitted')

    def test_unrecall_to_processing_same_party(self):
        """
        Testing `unrecall_to_processing` transition using a party reporter user
        for a submission created by another user from the same party.
        Expected result: 200.
        """

        submission = self.create_submission(
            owner=self.reporter,
            party=self.party,
            current_state='recalled',
            previous_state='processing'
        )
        self.client.login(username=self.reporter_same_party.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='unrecall_to_processing'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'processing')

    def test_unrecall_to_finalized_same_party(self):
        """
        Testing `unrecall_to_finalized` transition using a party reporter user
        for a submission created by another user from the same party.
        Expected result: 200.
        """

        submission = self.create_submission(
            owner=self.reporter,
            party=self.party,
            current_state='recalled',
            previous_state='finalized'
        )
        self.client.login(username=self.reporter_same_party.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='unrecall_to_finalized'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'finalized')

    def test_unrecall_to_submitted_another_party(self):
        """
        Testing `unrecall_to_submitted` transition using a party reporter user
        for a submission created by another user from another party.
        Expected result: 403 Forbidden.
        """

        submission = self.create_submission(
            owner=self.reporter,
            party=self.party,
            current_state='recalled',
            previous_state='submitted'
        )
        self.client.login(username=self.reporter_another_party.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='unrecall_to_submitted'
        )
        self.assertEqual(resp.status_code, 403)

    def test_unrecall_to_processing_another_party(self):
        """
        Testing `unrecall_to_processing` transition using a party reporter user
        for a submission created by another user from another party.
        Expected result: 403 Forbidden.
        """

        submission = self.create_submission(
            owner=self.reporter,
            party=self.party,
            current_state='recalled',
            previous_state='processing'
        )
        self.client.login(username=self.reporter_another_party.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='unrecall_to_processing'
        )
        self.assertEqual(resp.status_code, 403)

    def test_unrecall_to_finalized_another_party(self):
        """
        Testing `unrecall_to_finalized` transition using a party reporter user
        for a submission created by another user from another party.
        Expected result: 403 Forbidden.
        """

        submission = self.create_submission(
            owner=self.reporter,
            party=self.party,
            current_state='recalled',
            previous_state='finalized'
        )
        self.client.login(username=self.reporter_another_party.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='unrecall_to_finalized'
        )
        self.assertEqual(resp.status_code, 403)

    def test_finalize_write_secretariat(self):
        """
        Testing `process` transition using a secretariat user with write permissions.
        Expected result: 200.
        """

        submission = self.create_submission(
            owner=self.secretariat_user,
            party=self.party,
            current_state='processing',
            flag_valid=True
        )
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='finalize'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'finalized')

    def test_finalize_ro_secretariat(self):
        """
        Testing `process` transition using a secretariat user with read only
        permissions.
        Expected result: 403 Forbidden.
        """

        submission = self.create_submission(
            owner=self.secretariat_user,
            party=self.party,
            current_state='processing',
            flag_valid=True
        )
        self.client.login(username=self.secretariat_user_ro.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='finalize'
        )
        self.assertEqual(resp.status_code, 403)


class AcceleratedWorkflowTests(BaseWorkflowPermissionsTests):

    def setUp(self):
        super().setUp()
        self.workflow_class = 'accelerated'

    def test_finalize_write_secretariat(self):
        """
        Testing `finalize` transition using a secretariat user with write permissions.
        Expected result: 200.
        """

        submission = self.create_submission(
            owner=self.secretariat_user,
            party=self.party,
            current_state='data_entry'
        )
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
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

        submission = self.create_submission(
            owner=self.secretariat_user,
            party=self.party,
            current_state='data_entry'
        )
        self.client.login(username=self.secretariat_user_ro.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='finalized'
        )
        self.assertEqual(resp.status_code, 403)

    def test_recall_write_secretariat(self):
        """
        Testing `recall` transition using a secretariat user with write permissions.
        Expected result: 200.
        """

        submission = self.create_submission(
            owner=self.secretariat_user,
            party=self.party,
            current_state='finalized'
        )
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
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

        submission = self.create_submission(
            owner=self.secretariat_user,
            party=self.party,
            current_state='finalized'
        )
        self.client.login(username=self.secretariat_user_ro.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='recall'
        )
        self.assertEqual(resp.status_code, 403)

    def test_unrecall_write_secretariat(self):
        """
        Testing `unrecall` transition using a secretariat user with write permissions.
        Expected result: 200.
        """

        submission = self.create_submission(
            owner=self.secretariat_user,
            party=self.party,
            current_state='recalled'
        )
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
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

        submission = self.create_submission(
            owner=self.secretariat_user,
            party=self.party,
            current_state='recalled'
        )
        self.client.login(username=self.secretariat_user_ro.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='unrecall'
        )
        self.assertEqual(resp.status_code, 403)


EXEMPTION_NOMINATION_DATA = {
    "quantity": 100,
    "remarks_os": "nothing to remark OS",
}

EXEMPTION_APPROVED_DATA = {
    "quantity": 100,
    "remarks_os": "nothing to remark OS",
    "decision_approved": "it's a test"
}


class DefaultExemptionWorkflowTests(BaseWorkflowPermissionsTests):

    def setUp(self):
        super().setUp()
        self.workflow_class = 'default_exemption'
        self.substance = SubstanceFactory()

    def test_submit_secretariat(self):
        """
        Testing `submit` transition using a secretariat user for a submission
        created by the same secretariat user.
        Expected result: 200.
        """

        submission = self.create_submission(
            owner=self.secretariat_user,
            party=self.party,
            current_state='data_entry'
        )
        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='submit'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'submitted')

    def test_submit_reporter(self):
        """
        Testing `submit` transition using a party reporter user for a submission
        created by the same party reporter user.
        Expected result: 200.
        """

        submission = self.create_submission(
            owner=self.reporter,
            party=self.party,
            current_state='data_entry'
        )
        self.client.login(username=self.reporter_same_party.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='submit'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'submitted')

    def test_process_secretariat(self):
        """
        Testing `process` transition using a secretariat user for
        a submission created by the same secretariat user.
        Expected result: 200.
        """

        submission = self.create_submission(
            owner=self.secretariat_user,
            party=self.party,
            current_state='submitted'
        )

        NominationFactory(
            submission=submission, substance=self.substance,
            **EXEMPTION_NOMINATION_DATA
        )

        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='process'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'processing')

    def test_process_reporter(self):
        """
        Testing `process` transition using a party reporter user for
        a submission created by the same party reporter user.
        Expected result: 412 Only secretariat users can make this transition.
        """

        submission = self.create_submission(
            owner=self.reporter,
            party=self.party,
            current_state='submitted'
        )

        NominationFactory(
            submission=submission, substance=self.substance,
            **EXEMPTION_NOMINATION_DATA
        )

        self.client.login(username=self.reporter.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='process'
        )
        self.assertEqual(resp.status_code, 412)

    def test_finalize_approved_secretariat(self):
        """
        Testing `finalize` transition, for an approved nomination, using a
        secretariat user for a submission created by the same secretariat user.
        Expected result: 200.
        """

        submission = self.create_submission(
            owner=self.secretariat_user,
            party=self.party,
            current_state='processing',
            flag_approved=True
        )

        ExemptionApprovedFactory(
            submission=submission, substance=self.substance,
            **EXEMPTION_APPROVED_DATA
        )

        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='finalize'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'finalized')

    def test_finalize_no_data_secretariat(self):
        """
        Testing `finalize` transition without exempted data, using a
        secretariat user for a submission created by the same secretariat user.
        Expected result: 412.
        """

        submission = self.create_submission(
            owner=self.secretariat_user,
            party=self.party,
            current_state='processing',
            flag_approved=True
        )

        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='finalize'
        )
        self.assertEqual(resp.status_code, 412)

    def test_finalize_not_approved_secretariat(self):
        """
        Testing `finalize` transition, for a refused nomination, using a
        secretariat user for a submission created by the same secretariat user.
        Expected result: 412.
        """

        submission = self.create_submission(
            owner=self.secretariat_user,
            party=self.party,
            current_state='processing',
            flag_approved=False
        )

        ExemptionApprovedFactory(
            submission=submission, substance=self.substance,
            **EXEMPTION_APPROVED_DATA
        )

        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='finalize'
        )
        self.assertEqual(resp.status_code, 412)

    def test_finalize_not_approved_no_data_secretariat(self):
        """
        Testing `finalize` transition, for a refused nomination but with no data,
        using a secretariat user for a submission created by the same secretariat user.
        Expected result: 200.
        """

        submission = self.create_submission(
            owner=self.secretariat_user,
            party=self.party,
            current_state='processing',
            flag_approved=False
        )

        self.client.login(username=self.secretariat_user.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='finalize'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['current_state'], 'finalized')

    def test_finalize_party_reporter(self):
        """
        Testing `finalize` transition, using a party reporter user for
        a submission created by the same party reporter user.
        Expected result: 412 Only secretariat users can make this transition.
        """

        submission = self.create_submission(
            owner=self.reporter,
            party=self.party,
            current_state='processing',
            flag_approved=True
        )

        ExemptionApprovedFactory(
            submission=submission, substance=self.substance,
            **EXEMPTION_APPROVED_DATA
        )

        self.client.login(username=self.reporter.username, password='qwe123qwe')
        resp = self.call_transition(
            submission=submission,
            transition='finalize'
        )
        self.assertEqual(resp.status_code, 412)
