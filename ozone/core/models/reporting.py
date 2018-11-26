import enum

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from model_utils import FieldTracker

from .legal import ReportingPeriod
from .party import Party
from .utils import model_to_dict
from .workflows.base import BaseWorkflow
from .workflows.default import DefaultArticle7Workflow
from .workflows.accelerated import AcceleratedArticle7Workflow

__all__ = [
    'Obligation',
    'Submission',
    'TransitionEvent'
]


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

    # The type of form used to submit data. This will possibly get more complicated
    # in the future (e.g. when different forms will be necessary for the same obligation
    # but different reporting periods due to changes in the methodology
    form_type = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Submission(models.Model):
    """
    One specific data submission (version!)
    """

    @enum.unique
    class SubmissionMethods(enum.Enum):
        """
        Enumeration of submission types
        """
        WEBFORM = 'Web form'
        EMAIL = 'Email'

    class StateDoesNotExist(Exception):
        pass

    class TransitionDoesNotExist(Exception):
        pass

    class TransitionNotAvailable(Exception):
        pass

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
    # data might be received through physical mail; also, OS might decide to
    # make minor modifications on Party's submissions.
    filled_by_secretariat = models.BooleanField(default=False)

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

    flag_provisional = models.BooleanField(default=False)
    flag_valid = models.NullBooleanField(default=None)
    flag_superseded = models.BooleanField(default=False)

    submitted_via = models.CharField(
        max_length=32,
        choices=((s.value, s.name) for s in SubmissionMethods)
    )

    # We want these to be able to be empty in forms
    remarks_party = models.CharField(max_length=512, blank=True)
    remarks_secretariat = models.CharField(max_length=512, blank=True)

    # Needed to track state changes and help with custom logic
    tracker = FieldTracker()

    @property
    def workflow_class(self):
        """Just a getter so we can access the class"""
        return self._workflow_class

    @property
    def workflow(self):
        """
        Creates workflow instance and set last *persisted* state on it
        """
        wf = self.WORKFLOW_MAP[self._workflow_class](model_instance=self)
        state = self.tracker.previous('_current_state') \
            if self.tracker.has_changed('_current_state') \
            else self.current_state
        wf.state = state or wf.state.workflow.initial_state
        return wf

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, value):
        """
        Changing current_state also changes previous_state as a side effect.
        All state changes trigger an automatic save().

        Changing the state is done by calling the appropriate transition
        (if available) on the related workflow-enabled object (self.workflow).

        """
        workflow = self.workflow
        if value not in workflow.state.workflow.states:
            raise self.StateDoesNotExist(
                f'No state named {value} in current workflow'
            )

        transition_name = None
        for t in workflow.state.transitions():
            if value == t.target.name:
                transition_name = t.name
                break
        if transition_name is None:
            raise self.TransitionNotAvailable(
                f'No transition to reach {value} from current state'
            )

        transition = getattr(workflow, transition_name)

        if not transition.is_available():
            raise self.TransitionNotAvailable('Transition checks not satisfied')

        # Call the transition; this should work (bar exceptions in pre-post
        # transition hooks)
        transition()

        # If everything went OK, persist the result and the transition.
        self._previous_state = self._current_state
        self._current_state = workflow.state.name
        self.save()
        TransitionEvent.objects.create(
            submission=self,
            transition=transition_name,
            from_state=self._previous_state,
            to_state=self._current_state,
        )

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
        return self.workflow.data_changes_allowed

    @property
    def available_transitions(self):
        """
        List of transitions that can be performed from current state.

        """

        transitions = []
        wf = self.workflow
        for transition in wf .state.transitions():
            if hasattr(wf, 'check_' + transition.name):
                if getattr(wf, 'check_' + transition.name)():
                    transitions.append(transition.name)
            else:
                transitions.append(transition.name)
        return transitions

    @property
    def available_states(self):
        """
        List of states that can be reached directly from current state.
        No pre-transition checks are taken into account at this point.

        """
        return [t.target.name for t in self.workflow.state.transitions()]

    @property
    def editable_states(self):
        return self.workflow.editable_data_states

    @property
    def is_current(self):
        if (
            self.flag_superseded
            or self.current_state == self.workflow.state.workflow.initial_state.name
        ):
            return False
        return True

    def call_transition(self, trans_name, user):
        """
        Interface for calling a specific transition name on the workflow.

        It automatically persists the previous and new states, by saving the
        entire instance!

        """
        # Call this now so we don't recreate the self.workflow object ad nauseam
        workflow = self.workflow

        # This is a `TransitionList` and supports the `in` operator
        if trans_name not in workflow.state.workflow.transitions:
            raise self.TransitionDoesNotExist(
                f'Transition {trans_name} does not exist in this workflow'
            )

        # This is a list of `Transition`s and doesn't support the `in` operator
        # without explicitly referencing `name`
        if trans_name not in [t.name for t in workflow.state.transitions()]:
            raise self.TransitionNotAvailable(
                f'Transition {trans_name} does not start from current state'
            )

        # Transition names are available as attributes on the workflow object
        transition = getattr(workflow, trans_name)

        if not transition.is_available():
            raise self.TransitionNotAvailable('Transition checks not satisfied')

        # Call the transition; this should work (bar exceptions in pre-post
        # transition hooks)
        transition()

        # If everything went OK, persist the result and the transition.
        self._previous_state = self._current_state
        self._current_state = workflow.state.name
        self.save()
        TransitionEvent.objects.create(
            submission=self,
            transition=trans_name,
            from_state=self._previous_state,
            to_state=self._current_state,
            triggered_by=user
        )

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

    def check_cloning(self):
        """
        Checks whether the current submission can be cloned
        """
        if self.reporting_period.start_date > ReportingPeriod.current_period().end_date:
            raise ValidationError(
                _(
                    "You can't clone a submission from a following period"
                )
            )

        if self not in Submission.objects.filter(
            reporting_period=ReportingPeriod.current_period()
        ):
            if not (
                self.current_state == "finalized"
                and self.flag_valid is True
                and self.flag_superseded is False
            ):
                raise ValidationError(
                    _(
                        "You can't clone a submission from a previous period if "
                        "it's not a final version (finalized, valid, not superseded."
                    )
                )
        return True

    def clone(self):
        clone = Submission.objects.create(
            party=self.party,
            reporting_period=self.reporting_period,
            obligation=self.obligation,
            cloned_from=self,
            created_by=self.created_by,
            last_edited_by=self.last_edited_by
        )

        """
        We treat Article7Questionnaire separately because it has a one-to-one
        relation with submission and this way we avoid nasty verifications
        """
        exclude = [
            'id', 'submission_id', '_state', '_deferred_fields', '_tracker', 'save'
        ]
        if (
            hasattr(self, "article7questionnaire")
            and self.article7questionnaire is not None
        ):
            attributes = model_to_dict(self.article7questionnaire, exclude=exclude)
            attributes['submission_id'] = clone.pk
            self.article7questionnaire.__class__.objects.create(**attributes)

        for related_data in self.RELATED_DATA:
            for instance in getattr(self, related_data).all():
                if hasattr(instance, 'blend_item') and instance.blend_item is not None:
                    continue
                attributes = model_to_dict(instance, exclude=exclude)
                attributes['submission_id'] = clone.pk
                instance.__class__.objects.create(**attributes)

        return clone

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
            raise RuntimeError(
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
        if self.non_exempted_fields_modified() and not self.data_changes_allowed:
            raise ValidationError(
                _("Submitted submissions cannot be modified.")
            )
        super().clean()

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Auto-increment submission version if saving for a
        # party-obligation-reporting_period combo which already has submissions.
        # select_for_update() is used to lock the rows and ensure proper
        # concurrency.
        if not self.pk:
            submissions = Submission.objects.select_for_update().filter(
                party=self.party,
                reporting_period=self.reporting_period,
                obligation=self.obligation
            )
            if any([s.data_changes_allowed for s in submissions]):
                raise ValidationError(
                    _(
                        "There is already a submission in Data Entry for "
                        "this party/period/obligation combination"
                    )
                )
            if submissions:
                self.version = submissions.latest('version').version + 1

        # TODO: this is not such a nice verification of first save
        # On first save we need to instantiate the submission's workflow
        if not self.pk or kwargs.get('force_insert', False):
            # TODO: get the proper workflow based on obligation and context
            # (e.g. fast-tracked secretariat submissions).
            # For now we will naively instantiate all submissions with
            # the default article 7 workflow.
            self._workflow_class = 'default'
            self._current_state = \
                self.workflow.state.workflow.initial_state.name

        self.clean()
        return super().save(*args, **kwargs)

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


class TransitionEvent(models.Model):
    """
    Generic transition events in a submission's life cycle.
    """
    submission = models.ForeignKey(
        Submission, related_name='transition_events' ,on_delete=models.PROTECT
    )

    timestamp = models.DateTimeField(auto_now_add=True, editable=False)

    transition = models.CharField(max_length=60)
    from_state = models.CharField(max_length=60)
    to_state = models.CharField(max_length=60)
    triggered_by = models.ForeignKey(
        get_user_model(),
        related_name='transitions_triggered',
        on_delete=models.PROTECT
    )
    extra = JSONField(encoder=DjangoJSONEncoder, null=True)

    class Meta:
        verbose_name = 'workflow event'
        unique_together = ('timestamp', 'submission', 'from_state', 'to_state')
