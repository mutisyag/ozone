from django.core.validators import MinValueValidator
from django.db import models

from .party import Party
from .reporting import Submission
from .substance import Substance
from .meeting import Decision
from .utils import DECIMAL_FIELD_DECIMALS, DECIMAL_FIELD_DIGITS

__all__ = [
    'ProcessAgentContainTechnology',
    'ProcessAgentApplication',
    'ProcessAgentUsesReported',
    'ProcessAgentEmissionLimit',
    'ProcessAgentApplicationValidity',
    'ProcessAgentEmissionLimitValidity',
]


class ProcessAgentContainTechnology(models.Model):
    """
    Reported containment technologies
    """

    description = models.CharField(max_length=9999)

    def __str__(self):
        return self.description

    class Meta:
        verbose_name_plural = 'process agent contain technologies'
        db_table = 'pa_contain_technology'


class ProcessAgentApplicationValidityManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related(
            'decision',
        )


class ProcessAgentApplicationValidity(models.Model):

    objects = ProcessAgentApplicationValidityManager()

    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    decision = models.OneToOneField(
        Decision,
        related_name='applications_validity',
        on_delete=models.PROTECT
    )

    def __str__(self):
        start_year = self.start_date.year if self.start_date else "N/A"
        end_year = self.end_date.year if self.end_date else "N/A"
        return f"{self.decision.decision_id} ({start_year}-{end_year})"

    class Meta:
        verbose_name_plural = 'process agent applications validity'
        db_table = 'pa_applications_validity'


class ProcessAgentApplicationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related(
            'substance', 'validity', 'validity__decision',
        )


class ProcessAgentApplication(models.Model):
    """
    Applications of controlled substances as process agents, as approved
    in table A of decision X/14 and updated periodically by the Meeting of the
    Parties.
    """

    objects = ProcessAgentApplicationManager()

    validity = models.ForeignKey(
        ProcessAgentApplicationValidity,
        related_name='pa_applications',
        on_delete=models.PROTECT
    )

    counter = models.PositiveIntegerField()

    substance = models.ForeignKey(Substance, on_delete=models.PROTECT)

    application = models.CharField(max_length=256)

    remark = models.CharField(max_length=9999, blank=True)

    def __str__(self):
        return f'{self.substance} - {self.application}'

    class Meta:
        db_table = 'pa_application'


class ProcessAgentUsesReportedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related(
            'submission', 'submission__party', 'submission__reporting_period',
            'decision', 'application', 'application__substance',
        )


class ProcessAgentUsesReported(models.Model):
    """
    Records information on process agent uses reported.
    """
    UNITS = (
        ('MT', 'Metric Tonnes'),
        ('ODP tonnes', 'ODP Tonnes')
    )

    objects = ProcessAgentUsesReportedManager()

    submission = models.ForeignKey(
        Submission,
        related_name='pa_uses_reported',
        on_delete=models.PROTECT
    )

    decision = models.ForeignKey(
        Decision,
        related_name='pa_uses_reported',
        null=True,
        blank=True,
        on_delete=models.PROTECT
    )

    application = models.ForeignKey(
        ProcessAgentApplication,
        related_name='pa_uses_reported',
        blank=True,
        null=True,
        on_delete=models.PROTECT
    )

    contain_technologies = models.ManyToManyField(
        ProcessAgentContainTechnology,
        blank=True,
    )

    makeup_quantity = models.DecimalField(
        max_digits=DECIMAL_FIELD_DIGITS, decimal_places=DECIMAL_FIELD_DECIMALS,
        validators=[MinValueValidator(0.0)],
        null=True,
        blank=True
    )

    emissions = models.DecimalField(
        max_digits=DECIMAL_FIELD_DIGITS, decimal_places=DECIMAL_FIELD_DECIMALS,
        validators=[MinValueValidator(0.0)],
        null=True,
        blank=True
    )

    units = models.CharField(
        max_length=64,
        choices=UNITS,
        null=True,
        blank=True
    )

    remark = models.CharField(max_length=9999, blank=True)

    def __str__(self):
        if self.application:
            return (
                f'{self.submission.party} - Process agent reported use of '
                f'{self.application.substance} for '
                f'{self.submission.reporting_period.name}'
            )
        return (
            f'{self.submission.party} - Process agent reported use for '
            f'{self.submission.reporting_period.name}'
        )

    class Meta:
        verbose_name_plural = 'process agent uses reported'
        db_table = 'pa_uses_reported'


class ProcessAgentEmissionLimitValidity(models.Model):
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    decision = models.OneToOneField(
        Decision,
        related_name='limits_validity',
        on_delete=models.PROTECT
    )

    def __str__(self):
        start_year = self.start_date.year if self.start_date else "N/A"
        end_year = self.end_date.year if self.end_date else "N/a"
        return f"{self.decision.decision_id} {start_year}-{end_year}"

    class Meta:
        verbose_name_plural = 'process agent emission limits validity'
        db_table = 'pa_emission_limit_validity'


class ProcessAgentEmissionLimit(models.Model):
    """
    Emission limits for process agent uses, for non-Article 5 parties.
    """

    party = models.ForeignKey(
        Party,
        related_name='process_agent_emission_limits',
        on_delete=models.PROTECT
    )

    validity = models.ForeignKey(
        ProcessAgentEmissionLimitValidity,
        related_name='pa_emission_limits',
        on_delete=models.PROTECT
    )

    makeup_consumption = models.DecimalField(
        max_digits=DECIMAL_FIELD_DIGITS, decimal_places=DECIMAL_FIELD_DECIMALS,
        validators=[MinValueValidator(0.0)]
    )

    max_emissions = models.DecimalField(
        max_digits=DECIMAL_FIELD_DIGITS, decimal_places=DECIMAL_FIELD_DECIMALS,
        validators=[MinValueValidator(0.0)]
    )

    remark = models.CharField(max_length=9999, blank=True)

    class Meta:
        db_table = 'limit_pa_emission'
