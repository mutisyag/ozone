import enum
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from model_utils import FieldTracker
from simple_history.models import HistoricalRecords

from .legal import ReportingPeriod
from .party import Party
from .utils import model_to_dict
from .workflows.base import BaseWorkflow
from .workflows.default import DefaultArticle7Workflow
from .workflows.accelerated import AcceleratedArticle7Workflow
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
]

SUBMISSION_ROOT_DIR = 'submissions'


class ModifyPreventionMixin:
    """
    Mixin to be used by models with foreign keys to Submissions which need to
    prevent changes when the referenced submission is not in Data Entry.
    """

    def clean(self):
        if not self.submission.data_changes_allowed:
            raise ValidationError(
                _("Submitted submissions cannot be modified.")
            )
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Obligation(models.Model):
    """
    TODO: analysis!
    """

    name = models.CharField(max_length=256, unique=True)
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
    form_type = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class ReportingChannel(models.Model):
    """
    Model for storing submission types.
    """

    name = models.CharField(unique=True, max_length=256)
    description = models.CharField(max_length=256, blank=True)


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
        'accelerated': AcceleratedArticle7Workflow
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
        'transfers'
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
    submitted_at = models.DateTimeField(null=True)

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
    flag_provisional = models.BooleanField(default=False)
    flag_valid = models.NullBooleanField(default=None)
    flag_superseded = models.BooleanField(default=False)
    flag_checked_blanks = models.BooleanField(default=True)
    flag_has_blanks = models.BooleanField(default=False)
    flag_confirmed_blanks = models.BooleanField(default=False)
    flag_has_reported_a1 = models.BooleanField(default=True)
    flag_has_reported_a2 = models.BooleanField(default=True)
    flag_has_reported_b1 = models.BooleanField(default=True)
    flag_has_reported_b2 = models.BooleanField(default=True)
    flag_has_reported_b3 = models.BooleanField(default=True)
    flag_has_reported_c1 = models.BooleanField(default=True)
    flag_has_reported_c2 = models.BooleanField(default=True)
    flag_has_reported_c3 = models.BooleanField(default=True)
    flag_has_reported_e = models.BooleanField(default=True)
    # TODO: why is the default here False? does it have other implications?
    flag_has_reported_f = models.BooleanField(default=False)

    # We want these to be able to be empty in forms
    remarks_party = models.CharField(max_length=9999, blank=True)
    remarks_secretariat = models.CharField(max_length=9999, blank=True)

    # Art7 Remarks
    imports_remarks_party = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the reporting party for "
                  "imports"
    )
    imports_remarks_secretariat = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the ozone secretariat for "
                  "imports"
    )
    exports_remarks_party = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the reporting party for "
                  "exports"
    )
    exports_remarks_secretariat = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the ozone secretariat for "
                  "exports"
    )
    production_remarks_party = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the reporting party for "
                  "production"
    )
    production_remarks_secretariat = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the ozone secretariat for "
                  "production"
    )
    destruction_remarks_party = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the reporting party for "
                  "destruction"
    )
    destruction_remarks_secretariat = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the ozone secretariat for "
                  "destruction"
    )
    nonparty_remarks_party = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the reporting party for "
                  "nonparty"
    )
    nonparty_remarks_secretariat = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the ozone secretariat for "
                  "nonparty"
    )
    emissions_remarks_party = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the reporting party for "
                  "emissions"
    )
    emissions_remarks_secretariat = models.CharField(
        max_length=9999, blank=True,
        help_text="General Article7 obligation remarks added by the ozone secretariat for "
                  "emissions"
    )
    # HAT Remarks
    hat_production_remarks_party = models.CharField(
        max_length=9999, blank=True,
        help_text="General HAT obligation remarks added by the reporting party for "
                  "production"
    )
    hat_production_remarks_secretariat = models.CharField(
        max_length=9999, blank=True,
        help_text="General HAT obligation remarks added by the ozone secretariat for "
                  "production"
    )
    hat_imports_remarks_party = models.CharField(
        max_length=9999, blank=True,
        help_text="General HAT obligation remarks added by the reporting party for imports"
    )
    hat_imports_remarks_secretariat = models.CharField(
        max_length=9999, blank=True,
        help_text="General HAT obligation remarks added by the ozone secretariat for imports"
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
    def is_current(self):
        if (
            self.flag_superseded
            or self.current_state == self.workflow().state.workflow.initial_state.name
        ):
            return False
        return True

    def is_cloneable(self, user):
        is_cloneable, message = self.check_cloning(user)
        return is_cloneable

    def available_transitions(self, user):
        """
        List of transitions that can be performed from current state.

        """

        transitions = []
        wf = self.workflow(user)
        for transition in wf .state.transitions():
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
        # transition hooks)
        transition()

        # If everything went OK, persist the result and the transition.
        self._previous_state = self._current_state
        self._current_state = workflow.state.name
        self.save()

    def get_changeable_flags(self, user):
        """
        Returns list of flags that can be changed by the current user in the
        current state.
        N.B.: flag_superseded cannot be changed directly by users, it is
        only changed automatically by the system.
        """
        flags_list = []
        if user.is_secretariat:
            flags_list.extend([
                'flag_provisional', 'flag_checked_blanks',
                'flag_has_blanks', 'flag_confirmed_blanks',
                'flag_has_reported_a1', 'flag_has_reported_a2',
                'flag_has_reported_b1', 'flag_has_reported_b2',
                'flag_has_reported_b3', 'flag_has_reported_c1',
                'flag_has_reported_c2', 'flag_has_reported_c3',
                'flag_has_reported_e', 'flag_has_reported_f',
            ])
            if not self.data_changes_allowed:
                # valid flag can only be set after submitting
                flags_list.append('flag_valid')
        else:
            # Party user
            if self.data_changes_allowed:
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

            if not self.filled_by_secretariat and user.is_secretariat and field_name.endswith("_party"):
                # Secretariat users cannot modify any of the party fields, if the
                # submission was filled by a party.
                wrongly_modified_remarks.append(field_name)
            elif not user.is_secretariat and field_name.endswith("_secretariat"):
                # Party users cannot modify any of the secretariat remark fields
                wrongly_modified_remarks.append(field_name)

        if len(wrongly_modified_remarks) > 0:
            raise ValidationError({
                field: [_('User is not allowed to change this remark')]
                for field in wrongly_modified_remarks
            })
        return True

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
        ]

    def non_exempted_fields_modified(self):
        """
        Checks whether one of the non-exempted fields was modified.
        """
        exempted_fields = Submission.get_exempted_fields()
        modified_fields = self.tracker.changed()
        for field in modified_fields.keys():
            if field not in exempted_fields:
                return True
        return False

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
        # All non-data-entry submissions for open rep. periods can be cloned
        if self.data_changes_allowed:
            return (
                False,
                ValidationError(
                    _("Submission in Data Entry cannot be cloned.")
                )
            )

        return (True, None)

    def clone(self, user):
        is_cloneable, e = self.check_cloning(user)
        if is_cloneable:
            clone = Submission.objects.create(
                party=self.party,
                reporting_period=self.reporting_period,
                obligation=self.obligation,
                cloned_from=self,
                created_by=self.created_by,
                last_edited_by=self.last_edited_by,
            )
            if hasattr(self, 'info'):
                SubmissionInfo.objects.create(
                    submission=clone,
                    reporting_officer=self.info.reporting_officer,
                    designation=self.info.designation,
                    organization=self.info.organization,
                    postal_code=self.info.postal_code,
                    country=self.info.country,
                    phone=self.info.phone,
                    fax=self.info.fax,
                    email=self.info.email,
                    date=self.info.date,
                    reporting_channel=self.info.reporting_channel
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
        if self.non_exempted_fields_modified() and not self.data_changes_allowed:
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
            if any([s.data_changes_allowed for s in current_submissions]):
                raise ValidationError(
                    _(
                        "There is already a submission in Data Entry for "
                        "this party/period/obligation combination."
                    )
                )
            if current_submissions:
                self.version = current_submissions.latest('version').version + 1

            # On first save we need to instantiate the submission's workflow
            # TODO: get the proper workflow based on obligation and context
            # (e.g. fast-tracked secretariat submissions).
            # For now we will naively instantiate all submissions with
            # the default article 7 workflow.
            self._workflow_class = 'default'
            self._current_state = \
                self.workflow().state.workflow.initial_state.name

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
                        postal_code=latest_info.postal_code,
                        country=latest_info.country,
                        phone=latest_info.phone,
                        fax=latest_info.fax,
                        email=latest_info.email,
                        date=latest_info.date,
                        reporting_channel=ReportingChannel.objects.get(
                            name='Web form'
                        )
                    )
                else:
                    info = SubmissionInfo.objects.create(
                        submission=self,
                        reporting_channel=ReportingChannel.objects.get(
                            name='Web form'
                        )
                    )

            return ret

        else:
            # This is not the first save
            self.clean()
            return super().save(
                force_insert=force_insert, force_update=force_update,
                using=using, update_fields=update_fields
            )

    def set_submitted(self):
        self.submitted_at = timezone.now()
        self.save()


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
    postal_code = models.CharField(max_length=64, blank=True)
    country = models.CharField(max_length=256, blank=True)
    phone = models.CharField(max_length=128, blank=True)
    fax = models.CharField(max_length=128, blank=True)
    email = models.EmailField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    reporting_channel = models.ForeignKey(
        ReportingChannel,
        related_name="info",
        null=True,
        blank=True,
        on_delete=models.PROTECT
    )

    def __str__(self):
        return f'{self.submission} - Info'
