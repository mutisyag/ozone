import enum
import os

from datetime import datetime
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from model_utils import FieldTracker
from simple_history.models import HistoricalRecords

from .legal import ReportingPeriod
from .party import Party
from .utils import model_to_dict
from .workflows.base import BaseWorkflow
from .workflows.default import DefaultArticle7Workflow
from .workflows.accelerated import AcceleratedArticle7Workflow
from .workflows.default_exemption import DefaultExemptionWorkflow
from .workflows.accelerated_exemption import AcceleratedExemptionWorkflow
from ..exceptions import (
    Forbidden,
    MethodNotAllowed,
    TransitionDoesNotExist,
    TransitionNotAvailable,
)

__all__ = [
    'ModifyPreventionMixin',
    'Obligation',
    'Submission',
    'SubmissionInfo',
    'ReportingChannel',
    'SubmissionFormat',
]

SUBMISSION_ROOT_DIR = 'submissions'


class ModifyPreventionMixin:
    """
    Mixin to be used by models with foreign keys to Submissions which need to
    prevent changes when the referenced submission is not in Data Entry.
    """

    @staticmethod
    def get_exempted_fields():
        return [
            # Secretariat remarks can be changed
            # at any time, while the party remarks cannot.
            "remarks_os"
        ]

    def clean(self):
        if (
            Submission.non_exempted_fields_modified(self)
            and not self.submission.data_changes_allowed
        ):
            raise ValidationError(
                _("Submitted submissions cannot be modified.")
            )
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


@enum.unique
class FormTypes(enum.Enum):
    ART7 = 'art7'
    ESSENCRIT = 'essencrit'
    HAT = 'hat'
    OTHER = 'other'
    EXEMPTION = 'exemption'


class Obligation(models.Model):

    NOT_CLONEABLE = [
        'exemption',
    ]

    name = models.CharField(
        max_length=256, unique=True,
        help_text="A unique String value identifying this obligation."
    )
    # TODO: obligation-party mapping!

    description = models.CharField(max_length=256, blank=True)

    # Some obligations require immediate reporting each time an event happens,
    # instead of periodical reporting. This should get special treatment both
    # in backend and frontend.
    has_reporting_periods = models.BooleanField(default=True)

    # The type of form used to submit data.
    # This will possibly get more complicated in the future
    # (e.g. when different forms will be necessary for the same obligation
    # but different reporting periods due to changes in the methodology
    _form_type = models.CharField(
        max_length=64, choices=((s.value, s.name) for s in FormTypes),
        null=True,
        help_text="Used to generate the correct form, based on this obligation."
    )

    other = models.BooleanField(default=False)

    is_default = models.NullBooleanField(
        default=None,
        help_text="If set to true it means that the current obligation is used "
                  "as default for 'Data entry submissions' and 'All submissions' sections."
    )

    @property
    def form_type(self):
        return self._form_type

    def __str__(self):
        return self.name

    @classmethod
    def get_default(cls):
        return (
            cls.objects.filter(is_default=True)
            .first()
        )

    def clean(self):
        default_obligation_qs = Obligation.objects.filter(is_default=True)
        if (
            self.is_default
            and default_obligation_qs.count() > 0
            and self not in default_obligation_qs
        ):
            raise ValidationError(
                _('Only one obligation can be set as default.')
            )

    class Meta:
        db_table = "core_obligation"


class ReportingChannel(models.Model):
    """
    Describes the way the form was submitted.
    """

    name = models.CharField(unique=True, max_length=256)
    description = models.CharField(max_length=256, blank=True)

    class Meta:
        db_table = "reporting_channel"


class Submission(models.Model):
    """
    One specific data submission (version!)
    """

    # This keeps a mapping between the DB-persisted workflow and
    # its actual implementation class.
    WORKFLOW_MAP = {
        'empty': None,
        'base': BaseWorkflow,
        'default': DefaultArticle7Workflow,
        'accelerated': AcceleratedArticle7Workflow,
        'default_exemption': DefaultExemptionWorkflow,
        'accelerated_exemption': AcceleratedExemptionWorkflow
    }

    RELATED_DATA = [
        'article7exports',
        'article7imports',
        'article7productions',
        'article7destructions',
        'article7nonpartytrades',
        'article7emissions',
        'highambienttemperatureproductions',
        'highambienttemperatureimports',
        'transfers',
        'dataothers',
        'nominations',
        'exemptionapproveds',
        'rafreports',
    ]

    # TODO: this implements the `submission_type` field from the
    # Ozone Business Data Tables. Analyze how Party-to-Obligation/Version
    # mappings should be modeled.
    obligation = models.ForeignKey(
        Obligation, related_name='submissions', on_delete=models.PROTECT
    )

    # TODO (related to the above):
    # It looks like the simplest (best?) solution for handling
    # reporting format changes (i.e. schema versions) is to keep separate
    # models&tables for each such version.
    # Should investigate whether what's described above is a sane solution.
    schema_version = models.CharField(max_length=64)

    reporting_period = models.ForeignKey(
        ReportingPeriod, related_name='submissions', on_delete=models.PROTECT
    )

    # `party` is always the Party for which data is reported
    party = models.ForeignKey(
        Party, related_name='submissions', on_delete=models.PROTECT
    )

    # Is set only at *the first* transition to Submitted
    submitted_at = models.DateField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    created_by = models.ForeignKey(
        get_user_model(),
        related_name='submissions_created',
        on_delete=models.PROTECT
    )
    last_edited_by = models.ForeignKey(
        get_user_model(),
        related_name='submissions_last_edited',
        on_delete=models.PROTECT
    )

    # Per Obligation-ReportingPeriod-Party
    version = models.PositiveSmallIntegerField(default=1)

    cloned_from = models.ForeignKey(
        'self',
        related_name='clones',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    # Persisted workflow class for this submission. We want this to be only set
    # at submission creation, so it will have no setter implementation.
    _workflow_class = models.CharField(
        max_length=32,
        choices=((w, w.capitalize()) for w in WORKFLOW_MAP.keys()),
        default='empty',
        db_column='workflow_class'
    )
    # States will be accessed through properties to enable custom logic
    # on state transitions.
    # We will impose no restriction on state name choices, as there is no
    # way of knowing them before runtime. Instead, the associated workflow
    # object (`self.workflow`) will be responsible for sane transitions.
    _current_state = models.CharField(
        max_length=64, null=True, blank=True, db_column='current_state'
    )
    # We need previous_state for un-recalling submissions
    _previous_state = models.CharField(
        max_length=64, null=True, blank=True, db_column='previous_state'
    )

    # Flags
    flag_provisional = models.BooleanField(
        default=False,
        help_text="If set to true it signals that future changes are foreseen."
    )
    flag_valid = models.NullBooleanField(
        default=None,
        help_text="If set to true it signals that the data in the current "
        "version is considered correct. Can be set by the Secretariat during "
        "Processing or at the transition between the Processing or Finalized states."
    )
    flag_superseded = models.BooleanField(
        default=False,
        help_text="If set to true it means that the current version is not "
        "relevant anymore. When a newer version of data is Submitted, "
        "the current one is automatically flagged as Superseded."
    )
    flag_checked_blanks = models.BooleanField(default=True)
    flag_has_blanks = models.BooleanField(default=False)
    flag_confirmed_blanks = models.BooleanField(default=False)
    flag_has_reported_a1 = models.BooleanField(
        default=True,
        help_text="If set to true it means that substances under "
                  "Annex A Group 1 were reported."
    )
    flag_has_reported_a2 = models.BooleanField(
        default=True,
        help_text="If set to true it means that substances under "
                  "Annex A Group 2 were reported."
    )
    flag_has_reported_b1 = models.BooleanField(
        default=True,
        help_text="If set to true it means that substances under "
                  "Annex B Group 1 were reported."
    )
    flag_has_reported_b2 = models.BooleanField(
        default=True,
        help_text="If set to true it means that substances under "
                  "Annex B Group 2 were reported."
    )
    flag_has_reported_b3 = models.BooleanField(
        default=True,
        help_text="If set to true it means that substances under "
                  "Annex B Group 3 were reported."
    )
    flag_has_reported_c1 = models.BooleanField(
        default=True,
        help_text="If set to true it means that substances under "
                  "Annex C Group 1 were reported."
    )
    flag_has_reported_c2 = models.BooleanField(
        default=True,
        help_text="If set to true it means that substances under "
                  "Annex C Group 2 were reported."
    )
    flag_has_reported_c3 = models.BooleanField(
        default=True,
        help_text="If set to true it means that substances under "
                  "Annex C Group 3 were reported."
    )
    flag_has_reported_e = models.BooleanField(
        default=True,
        help_text="If set to true it means that substances under "
                  "Annex E were reported."
    )
    # TODO: why is the default here False? does it have other implications?
    flag_has_reported_f = models.BooleanField(
        default=False,
        help_text="If set to true it means that substances under "
                  "Annex F were reported."
    )

    # We want these to be able to be empty in forms
    remarks_party = models.CharField(max_length=9999, blank=True)
    remarks_secretariat = models.CharField(max_length=9999, blank=True)

    # Art7 Remarks
    questionnaire_remarks_party = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the reporting "
                  "party for questionnaire"
    )
    questionnaire_remarks_secretariat = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the ozone "
                  "secretariat for questionnaire"
    )
    imports_remarks_party = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the reporting "
                  "party for imports"
    )
    imports_remarks_secretariat = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the ozone "
                  "secretariat for imports"
    )
    exports_remarks_party = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the reporting "
                  "party for exports"
    )
    exports_remarks_secretariat = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the ozone "
                  "secretariat for exports"
    )
    production_remarks_party = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the reporting "
                  "party for production"
    )
    production_remarks_secretariat = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the ozone "
                  "secretariat for production"
    )
    destruction_remarks_party = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the reporting "
                  "party for destruction"
    )
    destruction_remarks_secretariat = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the ozone "
                  "secretariat for destruction"
    )
    nonparty_remarks_party = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the reporting "
                  "party for nonparty"
    )
    nonparty_remarks_secretariat = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the ozone "
                  "secretariat for nonparty"
    )
    emissions_remarks_party = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the reporting "
                  "party for emissions"
    )
    emissions_remarks_secretariat = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the ozone "
                  "secretariat for emissions"
    )
    # HAT Remarks
    hat_production_remarks_party = models.CharField(
        max_length=9999, blank=True,
        help_text="General HAT obligation remarks added by the reporting party "
                  "for production"
    )
    hat_production_remarks_secretariat = models.CharField(
        max_length=9999, blank=True,
        help_text="General HAT obligation remarks added by the ozone "
                  "secretariat for production"
    )
    hat_imports_remarks_party = models.CharField(
        max_length=9999, blank=True,
        help_text="General HAT obligation remarks added by the reporting party "
                  "for imports"
    )
    hat_imports_remarks_secretariat = models.CharField(
        max_length=9999, blank=True,
        help_text="General HAT obligation remarks added by the ozone "
                  "secretariat for imports"
    )
    # Exemption
    exemption_nomination_remarks_secretariat = models.CharField(
        max_length=9999, blank=True,
        help_text="Exemption nomination remarks added by the ozone secretariat"
    )
    exemption_approved_remarks_secretariat = models.CharField(
        max_length=9999, blank=True,
        help_text="Exemption approved remarks added by the ozone secretariat"
    )
    # RAF
    raf_remarks_party = models.CharField(
        max_length=9999, blank=True,
        help_text="General RAF remarks added by the reporting party"
    )
    raf_remarks_secretariat = models.CharField(
        max_length=9999, blank=True,
        help_text="General RAF remarks added by the ozone secretariat"
    )

    reporting_channel = models.ForeignKey(
        ReportingChannel,
        related_name="submission",
        null=True,
        blank=True,
        on_delete=models.PROTECT
    )

    # Exemption related flags
    flag_emergency = models.BooleanField(
        default=False,
        help_text="If set to true it means that ozone secretariat "
                  "can fill out only the Approved form directly."
    )
    flag_approved = models.NullBooleanField(
        default=None,
        help_text="If set to true it means that the nomination was approved."
    )

    # Needed to track state changes and help with custom logic
    tracker = FieldTracker()

    history = HistoricalRecords()

    @property
    def filled_by_secretariat(self):
        return self.created_by.is_secretariat

    @property
    def workflow_class(self):
        """Just a getter so we can access the class"""
        return self._workflow_class

    def workflow(self, user=None):
        """
        Creates workflow instance and set last *persisted* state on it
        """
        wf = self.WORKFLOW_MAP[self._workflow_class](
            model_instance=self,
            user=user
        )
        state = self.tracker.previous('_current_state') \
            if self.tracker.has_changed('_current_state') \
            else self.current_state
        wf.state = state or wf.state.workflow.initial_state
        return wf

    @property
    def current_state(self):
        return self._current_state

    @property
    def previous_state(self):
        """
        Previous state will only be changed indirectly when changing
        current_state; only a getter is needed.
        """
        return self._previous_state

    @property
    def data_changes_allowed(self):
        """
        Check whether data changes are allowed in current state.
        """
        return self.workflow().data_changes_allowed

    @property
    def available_states(self):
        """
        List of states that can be reached directly from current state.
        No pre-transition checks are taken into account at this point.

        """
        return [t.target.name for t in self.workflow().state.transitions()]

    @property
    def editable_states(self):
        return self.workflow().editable_data_states

    @property
    def in_initial_state(self):
        return self.workflow().in_initial_state

    @property
    def is_current(self):
        if self.flag_superseded or self.in_initial_state:
            return False
        return True

    def is_cloneable(self, user):
        is_cloneable, message = self.check_cloning(user)
        return is_cloneable

    def available_transitions(self, user):
        """
        List of transitions that can be performed from current state.

        """
        # Simply avoid needless processing
        if user.is_read_only:
            return []

        transitions = []
        wf = self.workflow(user)
        for transition in wf.state.transitions():
            if hasattr(wf, 'check_' + transition.name):
                if getattr(wf, 'check_' + transition.name)():
                    transitions.append(transition.name)
            else:
                transitions.append(transition.name)
        return transitions

    def call_transition(self, trans_name, user):
        """
        Interface for calling a specific transition name on the workflow.

        It automatically persists the previous and new states, by saving the
        entire instance!

        """
        # Call this now so we don't recreate the self.workflow object ad nauseam
        workflow = self.workflow(user)

        # This is a `TransitionList` and supports the `in` operator
        if trans_name not in workflow.state.workflow.transitions:
            raise TransitionDoesNotExist(
                _(f'Transition {trans_name} does not exist in this workflow')
            )

        # This is a list of `Transition`s and doesn't support the `in` operator
        # without explicitly referencing `name`
        if trans_name not in [t.name for t in workflow.state.transitions()]:
            raise TransitionNotAvailable(
                _(f'Transition {trans_name} does not start from current state')
            )

        # Transition names are available as attributes on the workflow object
        transition = getattr(workflow, trans_name)

        if not transition.is_available():
            raise TransitionNotAvailable(
                _(
                    "Transition checks not satisfied or "
                    "you may not have the necessary permissions"
                )
            )

        # Call the transition; this should work (bar exceptions in pre-post
        # transition hooks, which will get caught later down the line if they
        # occur)
        transition()

        # If everything went OK, persist the result and the transition.
        self._previous_state = self._current_state
        self._current_state = workflow.state.name
        self.save()

    def is_submittable(self):
        """
        Checks that all required info has been filled before submission.
        """
        if (
            self.info.reporting_officer is ''
            or self.info.postal_address is '' and self.info.email is None
            or self.filled_by_secretariat and self.submitted_at is None
        ):
            return False

        if (
            self.obligation.name == 'Article 7'
            and (
                not hasattr(self, "article7questionnaire")
                or self.article7questionnaire is None
            )
        ):
            return False

        return True

    def can_edit_flags(self, user):
        """
        Returns True if user can set *any* flags on this submission,
        based strictly on read/write rights and ownership
        (i.e. does not take submission state into account)
        """
        if (
            user.is_secretariat
            or (user.party == self.party and not self.filled_by_secretariat)
        ):
            return not user.is_read_only

    def get_changeable_flags(self, user):
        """
        Returns list of flags that can be changed by the current user in the
        current state.
        N.B.: flag_superseded cannot be changed directly by users, it is
        only changed automatically by the system.
        """
        # First do a quick check based on actual permissions
        if not self.can_edit_flags(user):
            return []

        flags_list = []
        if user.is_secretariat:
            flags_list.extend([
                'flag_provisional', 'flag_checked_blanks',
                'flag_has_blanks', 'flag_confirmed_blanks',
            ])
            if self.in_initial_state:
                flags_list.extend([
                    'flag_has_reported_a1', 'flag_has_reported_a2',
                    'flag_has_reported_b1', 'flag_has_reported_b2',
                    'flag_has_reported_b3', 'flag_has_reported_c1',
                    'flag_has_reported_c2', 'flag_has_reported_c3',
                    'flag_has_reported_e', 'flag_has_reported_f',
                ])
            else:
                # valid & approved flags can only be set after submitting
                flags_list.extend(['flag_valid', 'flag_approved',])
        else:
            # Party user
            if self.in_initial_state:
                flags_list.extend([
                    'flag_provisional',
                    'flag_has_reported_a1', 'flag_has_reported_a2',
                    'flag_has_reported_b1', 'flag_has_reported_b2',
                    'flag_has_reported_b3', 'flag_has_reported_c1',
                    'flag_has_reported_c2', 'flag_has_reported_c3',
                    'flag_has_reported_e', 'flag_has_reported_f',
                ])

        return flags_list

    def check_flags(self, user, flags):
        """
        Raise error if user has changed flags he was not allowed to change
        in the current state; return True otherwise.
        """
        wrongly_modified_flags = [
            field_name for field_name, value in flags.items()
            if field_name.startswith('flag_') and
            field_name not in self.get_changeable_flags(user) and
            getattr(self, field_name) != value
        ]
        if len(wrongly_modified_flags) > 0:
            raise ValidationError({
                field: [_('User is not allowed to change this flag')]
                for field in wrongly_modified_flags
            })
        return True

    def can_edit_remarks(self, user):
        """
        Returns True if user can edit at least one remark on this submission.
        This is based purely on submission ownership!
        """
        # Party users should be able to change party remarks even on
        # secretariat-filled submissions
        if user.is_secretariat or user.party == self.party:
            return not user.is_read_only

    def can_change_remark(self, user, field_name):
        """
        Verifies whether user can change remark field `field_name`, based on
        both submission ownership/permissions and remarks mappings (OS vs party)
        """
        # First do a quick check based purely on ownership
        if not self.can_edit_remarks(user):
            return False

        if self.current_state not in self.editable_states and field_name.endswith("_party"):
            # The user cannot modify any of the party fields, if the
            # submission isn't in an editable state (e.g. `data_entry`)
            return False
        if not self.filled_by_secretariat and user.is_secretariat and field_name.endswith("_party"):
            # Secretariat users cannot modify any of the party fields, if the
            # submission was filled by a party.
            return False
        elif not user.is_secretariat and field_name.endswith("_secretariat"):
            # Party users cannot modify any of the secretariat remark fields
            return False

        return True

    def check_remarks(self, user, remarks):
        """
        Raise error if the user has change any remarks he was not allowed to
        change.
        """

        wrongly_modified_remarks = []

        # XXX Logic duplicated in DataCheckRemarksMixInBase.check_remarks
        for field_name, new_value in remarks.items():
            if new_value == getattr(self, field_name):
                # No value changed
                continue

            if not self.can_change_remark(user, field_name):
                wrongly_modified_remarks.append(field_name)

        if len(wrongly_modified_remarks) > 0:
            raise ValidationError({
                field: [_('User is not allowed to change this remark')]
                for field in wrongly_modified_remarks
            })
        return True

    def check_reporting_channel_modified(self):
        if 'reporting_channel_id' in self.tracker.changed().keys():
            return True
        return False

    def can_change_reporting_channel(self, user):
        if user.is_secretariat and self.filled_by_secretariat:
            return not user.is_read_only and self.in_initial_state
        return False

    @staticmethod
    def has_read_rights_for_party(party, user):
        if (
            user.is_secretariat
            or user.party is not None and user.party == party
        ):
            return True
        return False

    def has_read_rights(self, user):
        return self.has_read_rights_for_party(self.party, user)

    @staticmethod
    def has_create_rights_for_party(party, user):
        if (
            user.is_secretariat
            or user.party is not None and user.party == party
        ):
            return not user.is_read_only
        return False

    def has_edit_rights(self, user):
        if (
            user.is_secretariat and self.filled_by_secretariat
            or user.party == self.party and not self.filled_by_secretariat
        ):
            return not user.is_read_only
        return False

    def can_edit_data(self, user):
        if self.has_edit_rights(user):
            return self.data_changes_allowed
        return False

    def can_upload_files(self, user):
        if self.has_edit_rights(user):
            return True
        return False

    @staticmethod
    def get_exempted_fields():
        """
        List of exempted fields - fields that can be modified no matter in what
        state the current submission is.
        """
        return [
            "_current_state",
            "_previous_state",
            "flag_provisional",
            "flag_valid",
            "flag_superseded",
            "flag_checked_blanks",
            "flag_has_blanks",
            "flag_confirmed_blanks",
            "flag_has_reported_a1",
            "flag_has_reported_a2",
            "flag_has_reported_b1",
            "flag_has_reported_b2",
            "flag_has_reported_b3",
            "flag_has_reported_c1",
            "flag_has_reported_c2",
            "flag_has_reported_c3",
            "flag_has_reported_e",
            "flag_has_reported_f",
            # Remarks, secretariat remarks can be change
            # at any time, while the party remarks cannot.
            # "questionnaire_remarks_party",
            "questionnaire_remarks_secretariat",
            # "imports_remarks_party",
            "imports_remarks_secretariat",
            # "exports_remarks_party",
            "exports_remarks_secretariat",
            # "production_remarks_party",
            "production_remarks_secretariat",
            # "destruction_remarks_party",
            "destruction_remarks_secretariat",
            # "nonparty_remarks_party",
            "nonparty_remarks_secretariat",
            # "emissions_remarks_party",
            "emissions_remarks_secretariat",
            # "hat_production_remarks_party",
            "hat_production_remarks_secretariat",
            # "hat_imports_remarks_party",
            "hat_imports_remarks_secretariat",
            # "raf_remarks_party",
            "raf_remarks_secretariat",
            "exemption_nomination_remarks_secretariat",
            "exemption_approved_remarks_secretariat",
            "reporting_channel_id",
            "flag_approved",
            "submitted_at",
        ]

    @staticmethod
    def non_exempted_fields_modified(obj):
        """
        Checks whether one of the non-exempted fields was modified.
        """
        exempted_fields = obj.__class__.get_exempted_fields()
        modified_fields = obj.tracker.changed()
        for field in modified_fields.keys():
            if field not in exempted_fields:
                return True
        return False

    @staticmethod
    def has_initial_state_peers_by_same_user_type(peers, user):
        """
        This is used for checking whether a submission has an initial state peer
        (same party-period-obligation combination) created by the same type
        (Secretariat, party) of user.
        At any time, only one submission in initial state can exist per
        type of user and party-period-obligation.
        Since this is also used in save(), it takes a queryset as argument;
        this should contain its peers. Caller must ensure that this is properly
        constructed.
        """
        actor = "Secretariat" if user.is_secretariat else "party"
        message = _(
            f"There is already a Data Entry submission created by {actor} for "
            f"this party/period/obligation combination."
        )
        for sub in peers:
            if sub.in_initial_state:
                if sub.filled_by_secretariat and user.is_secretariat:
                    return True, message
                if not sub.filled_by_secretariat and not user.is_secretariat:
                    return True, message
        return False, None

    def check_cloning(self, user):
        """
        Checks whether the current submission can be cloned and the current user
        has the necessary permissions.
        """

        if (
            user.is_read_only or
            not (user.is_secretariat or self.party == user.party)
        ):
            return (
                False,
                Forbidden(
                    _("You do not have permission to perform this action.")
                )
            )

        if self.obligation.form_type in self.obligation.NOT_CLONEABLE:
            return (
                False,
                ValidationError(
                    _(
                        "You can't clone a submission with this type of "
                        "obligation"
                    )
                )
            )

        # Only non-superseded "past" submissions can be cloned
        if not self.reporting_period.is_reporting_open:
            if self.flag_superseded:
                return (
                    False,
                    ValidationError(
                        _(
                            "You can't clone a submission from a previous "
                            "period if it's superseded."
                        )
                    )
                )

        # Submissions can't be cloned if there is already a data entry one
        # created by the same user type (OS, party) for the same
        # party-period-obligation
        peers = Submission.objects.filter(
            party=self.party,
            obligation=self.obligation,
            reporting_period=self.reporting_period
        )
        has_peers, message = self.has_initial_state_peers_by_same_user_type(
            peers, user
        )
        if has_peers:
            return False, ValidationError(message)

        return True, None

    def clone(self, user):
        is_cloneable, e = self.check_cloning(user)
        if is_cloneable:
            channel = ReportingChannel.objects.get(name='Web form')
            clone = Submission.objects.create(
                party=self.party,
                reporting_period=self.reporting_period,
                obligation=self.obligation,
                cloned_from=self,
                created_by=user,
                last_edited_by=user,
                reporting_channel=channel
            )
            if hasattr(self, 'info'):
                # Clone submission might already have some pre-populated
                # info due to how save() works. These need to be updated.
                SubmissionInfo.objects.update_or_create(
                    submission=clone,
                    defaults={
                        'reporting_officer': self.info.reporting_officer,
                        'designation': self.info.designation,
                        'organization': self.info.organization,
                        'postal_address': self.info.postal_address,
                        'country': self.info.country,
                        'phone': self.info.phone,
                        'email': self.info.email,
                        'date': self.info.date,
                        'submission_format': self.info.submission_format,
                    }
                )
        else:
            raise e

        # We treat Article7Questionnaire separately because it has a one-to-one
        # relation with submission and this way we avoid nasty verifications
        exclude = [
            'id', 'submission_id', '_state', '_deferred_fields', '_tracker',
            'save',
        ]
        if (
            hasattr(self, "article7questionnaire")
            and self.article7questionnaire is not None
        ):
            attributes = model_to_dict(
                self.article7questionnaire, exclude=exclude
            )
            attributes['submission_id'] = clone.pk
            self.article7questionnaire.__class__.objects.create(**attributes)

        for related_data in self.RELATED_DATA:
            for instance in getattr(self, related_data).all():
                if hasattr(instance, 'blend_item') and instance.blend_item:
                    continue
                attributes = model_to_dict(instance, exclude=exclude)
                attributes['submission_id'] = clone.pk
                instance.__class__.objects.create(**attributes)

        return clone

    def get_storage_directory(self):
        """
        This determines the location at which files related to the submission
        will be saved.
        """
        return os.path.join(
            SUBMISSION_ROOT_DIR,
            self.reporting_period.name,
            self.obligation.name,
            self.party.abbr,
            str(self.version)
        )

    def delete_disk_file(self, file_name):
        """
        Used to delete an existing file from disk.
        """
        env_file = os.path.join(
            self.get_storage_directory(),
            file_name
        )
        try:
            os.remove(env_file)
        except FileNotFoundError:
            pass

    @transaction.atomic()
    def make_current(self):
        versions = (
            Submission.objects.select_for_update()
            .filter(
                party=self.party,
                reporting_period=self.reporting_period,
                obligation=self.obligation,
            )
            .exclude(pk=self.pk)
            .exclude(_current_state__in=self.editable_states)
        )
        for version in versions:
            version.flag_superseded = True
            version.save()
        self.flag_superseded = False
        self.save()

    @property
    def versions(self):
        return Submission.objects.filter(
            party=self.party,
            reporting_period=self.reporting_period,
            obligation=self.obligation,
        )

    def has_filled_nominations(self):
        return self.nominations.exists()

    def has_filled_approved_exemptions(self):
        return self.exemptionapproveds.exists()

    def has_set_approved_flag(self):
        return self.flag_approved

    def is_emergency(self):
        return self.flag_emergency

    def can_change_submitted_at(self, user):
        return (
            not user.is_read_only
            and user.is_secretariat
            and self.filled_by_secretariat
            and self.in_initial_state
        )

    def is_submitted_at_visible(self, user):
        if user.is_secretariat:
            return True
        elif user.party is not None and user.party == self.party:
            return not self.data_changes_allowed

    def is_submitted_at_mandatory(self, user):
        return self.can_change_submitted_at(user)

    def is_submitted_at_automatically_filled(self, user):
        """
        Return True if the user is a Party Reporter.
        """
        return not user.is_secretariat

    def __str__(self):
        return f'{self.party.name} report on {self.obligation.name} ' \
               f'for {self.reporting_period.name} - version {self.version}'

    class Meta:
        # TODO: this constraint may not be true in the corner case of
        # obligations where reporting is done per-case (e.g. transfers).
        # It may happen that several transfers take place in the same
        # reporting period - this means that the constraint should be checked
        # using custom logic on save() rather than enforced here. Investigate!
        unique_together = (
            'party', 'reporting_period', 'obligation', 'version'
        )
        db_table = 'submission'

    def delete(self, *args, **kwargs):
        if not self.data_changes_allowed:
            raise MethodNotAllowed(
                _("Submitted submissions cannot be deleted.")
            )
        # We need to delete all related data entries before being able to
        # delete the submission. We leave it to the interface to ask "are you
        # sure?" to the user.
        for related_data in self.RELATED_DATA:
            related_qs = getattr(self, related_data).all()
            if related_qs:
                related_qs.delete()

        super().delete(*args, **kwargs)

    def clean(self):
        if not self.reporting_period.is_reporting_allowed:
            raise ValidationError(
                _("Reporting cannot be performed for this reporting period.")
            )
        if (
            Submission.non_exempted_fields_modified(self)
            and not self.data_changes_allowed
        ):
            raise ValidationError(
                _("Submitted submissions cannot be modified.")
            )
        super().clean()

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # Several actions need to be performed on first save
        # No need to check `update_fields`, since this is the first
        # save. If other fields are changed during an update, they
        # must be added to the `update_fields` list, since we are using
        # the PartialUpdateMixIn.
        if not self.pk or force_insert:
            # Auto-increment submission version if saving for a
            # party-obligation-period combo which already has submissions.
            # select_for_update() is used to lock the rows and ensure proper
            # concurrency.
            submissions = Submission.objects.select_for_update().filter(
                party=self.party,
                obligation=self.obligation
            )
            current_submissions = submissions.filter(
                reporting_period=self.reporting_period
            )
            # Check that OS and party have only one data_entry submission
            has_peers, message = self.has_initial_state_peers_by_same_user_type(
                current_submissions, self.created_by
            )
            if has_peers:
                raise ValidationError(message)

            if current_submissions:
                self.version = current_submissions.latest('version').version + 1

            # On first save we need to instantiate the submission's workflow
            # TODO: get the proper workflow based on obligation and context
            # (e.g. fast-tracked secretariat submissions).
            # For now we will naively instantiate all submissions with
            # the default article 7 workflow.
            if self.obligation.name == 'Exemption':
                self._workflow_class = 'default_exemption'
            else:
                self._workflow_class = 'default'
            self._current_state = \
                self.workflow().state.workflow.initial_state.name

            # The default value for reporting channel is 'Web form'
            # when creating a new submission
            self.reporting_channel = ReportingChannel.objects.get(
                name='Web form'
            )

            self.clean()
            ret = super().save(
                force_insert=force_insert, force_update=force_update,
                using=using, update_fields=update_fields
            )

            # Prefill "Submission info" with values from the most recent
            # submission when creating a new submission for the same obligation
            # and party.
            # The prefill will be skipped if it's a clone action.
            if not hasattr(self, 'info'):
                latest_submission = submissions.order_by('-updated_at').first()
                if latest_submission and hasattr(latest_submission, 'info'):
                    latest_info = latest_submission.info
                    info = SubmissionInfo.objects.create(
                        submission=self,
                        reporting_officer=latest_info.reporting_officer,
                        designation=latest_info.designation,
                        organization=latest_info.organization,
                        postal_address=latest_info.postal_address,
                        country=latest_info.country,
                        phone=latest_info.phone,
                        email=latest_info.email,
                        date=latest_info.date,
                        submission_format=latest_info.submission_format
                    )
                else:
                    info = SubmissionInfo.objects.create(submission=self)

            return ret

        else:
            # This is not the first save
            self.clean()
            return super().save(
                force_insert=force_insert, force_update=force_update,
                using=using, update_fields=update_fields
            )

    def set_submitted(self):
        self.submitted_at = datetime.now().date()
        self.save()


class SubmissionFormat(models.Model):
    """
    Describes type of submission.
    """

    name = models.CharField(unique=True, max_length=256)
    description = models.CharField(max_length=256, blank=True)

    class Meta:
        db_table = "submission_format"


class SubmissionInfo(ModifyPreventionMixin, models.Model):
    """
    Model for storing submission info.
    """

    submission = models.OneToOneField(
        Submission,
        related_name='info',
        on_delete=models.CASCADE
    )

    reporting_officer = models.CharField(max_length=256, blank=True)
    designation = models.CharField(max_length=256, blank=True)
    organization = models.CharField(max_length=256, blank=True)
    postal_address = models.CharField(max_length=512, blank=True)
    country = models.CharField(max_length=256, blank=True)
    phone = models.CharField(max_length=128, blank=True)
    email = models.EmailField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    submission_format = models.ForeignKey(
        SubmissionFormat,
        related_name="infos",
        null=True,
        blank=True,
        on_delete=models.PROTECT
    )

    tracker = FieldTracker()

    class Meta:
        db_table = "submission_info"

    def __str__(self):
        return f'{self.submission} - Info'
