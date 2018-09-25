import enum

from django.db import models

from ozone.users.models import User

from .party import Party


__all__ = [
    'ReportingPeriod',
    'Obligation',
    'ReportingObligationType',
    'SubmissionStatus',
    'Submission',
]


class ReportingPeriod(models.Model):
    """
    Period for which data is submitted.

    There is definitely a need to support non-standard reporting periods.
    """

    # TODO: how will these be used in the event of one-time reports?
    # The system could create a custom period based on the date(s) the transfer
    # took place, but that seems a bit overkill.

    # This will usually be '2017', '2018' etc; most periods (but not all!)
    # are mapped to calendar years
    name = models.CharField(max_length=64, unique=True)
    # indicates a "normal" (yearly) reporting period, to avoid need of extra
    # logic on the `name` field
    is_year = models.BooleanField(default=True)

    # this is always required, and can be in the future
    start_date = models.DateField()

    # we are always working with 'closed' reporting periods
    # TODO: is above assumption really true? what about one-time reports?
    end_date = models.DateField()

    description = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return self.name


class Obligation(models.Model):
    """
    TODO: analysis!
    """

    name = models.CharField(max_length=256, unique=True)
    # TODO: obligation-party mapping!

    is_continuous = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ReportingObligationType(models.Model):
    """
    List of reporting obligations that have a formal structure.
    """

    obligation_type_id = models.CharField(max_length=16, unique=True)

    name = models.CharField(max_length=256, unique=True)

    description = models.CharField(max_length=256, blank=True)


class SubmissionStatus(models.Model):
    """
    Model used for declaring states of a submission.
    """

    status_id = models.CharField(max_length=16, unique=True)

    name = models.CharField(max_length=256, unique=True)

    remark = models.CharField(max_length=256, blank=True)


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

    # TODO: this implements the `submission_type` field from the
    # Ozone Business Data Tables. Analyze how Party-to-Obligation/Version
    # mappings should be modeled.
    obligation = models.ForeignKey(
        Obligation, related_name='submissions', on_delete=models.PROTECT
    )
    obligation_type = models.ForeignKey(
        ReportingObligationType, related_name='submissions', on_delete=models.PROTECT
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
        User, related_name='submissions_created', on_delete=models.PROTECT
    )
    last_edited_by = models.ForeignKey(
        User, related_name='submissions_last_edited', on_delete=models.PROTECT
    )

    # per Obligation-ReportingPeriod-Party
    # TODO: auto-increment version on save()
    version = models.PositiveSmallIntegerField(default=1)

    # TODO: make this workflow-based, including logic on save()
    status = models.ForeignKey(
        SubmissionStatus, on_delete=models.PROTECT
    )

    flag_provisional = models.BooleanField(default=False)
    flag_valid = models.BooleanField(default=False)
    flag_superseded = models.BooleanField(default=False)

    submitted_via = models.CharField(
        max_length=32,
        choices=((s.value, s.name) for s in SubmissionMethods)
    )

    # We want these to be able to be empty in forms
    remarks_party = models.CharField(max_length=512, blank=True)
    remarks_secretariat = models.CharField(max_length=512, blank=True)

    def __str__(self):
        return f'{self.party.name} report on {self.obligation.name} ' \
               f'for {self.reporting_period.name} - version {self.version}'

    class Meta:
        # TODO: this constraint may not be true in the corner case of
        # obligations where reporting is done per-case (e.g. transfers).
        # It may happen that several transfers take place in the same
        # reporting period - this means that the constraint should be checked
        # using custom logic on save() rather than enforced here. Investigate!
        unique_together = ('party', 'reporting_period', 'obligation',
                           'version')
