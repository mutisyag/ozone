from django.core.validators import MinValueValidator
from django.db import models

from .party import Party
from .reporting import Submission
from .substance import Substance
from .meeting import Decision

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

    submission = models.ForeignKey(
        Submission,
        related_name='pa_contain_technologies',
        on_delete=models.PROTECT
    )

    contain_technology = models.CharField(max_length=9999)

    class Meta:
        verbose_name_plural = 'process agent contain technologies'
        db_table = 'pa_contain_technology'


class ProcessAgentApplicationValidity(models.Model):
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    decision = models.OneToOneField(
        Decision,
        related_name='uses_validity',
        on_delete=models.PROTECT
    )

    def __str__(self):
        start_year = self.start_date.year if self.start_date else "N/A"
        end_year = self.end_date.year if self.end_date else "N/A"
        return f"{self.decision.decision_id} {start_year}-{end_year}"

    class Meta:
        verbose_name_plural = 'process agent uses validity'
        db_table = 'pa_uses_validity'


class ProcessAgentApplication(models.Model):
    """
    Applications of controlled substances as process agents, as approved
    in table A of decision X/14 and updated periodically by the Meeting of the
    Parties.
    """

    validity = models.ForeignKey(
        ProcessAgentApplicationValidity,
        related_name='pa_applications',
        on_delete=models.PROTECT
    )

    counter = models.PositiveIntegerField()

    substance = models.ForeignKey(Substance, on_delete=models.PROTECT)

    application = models.CharField(max_length=256)

    remark = models.CharField(max_length=9999, blank=True)

    class Meta:
        db_table = 'pa_application'


class ProcessAgentUsesReported(models.Model):
    """
    Records information on process agent uses reported.
    """
    UNITS = (
        ('MT', 'Metric Tonnes'),
        ('ODP tonnes', 'ODP Tonnes')
    )

    submission = models.ForeignKey(
        Submission,
        related_name='pa_uses_reported',
        on_delete=models.PROTECT
    )

    validity = models.ForeignKey(
        ProcessAgentApplicationValidity,
        related_name='pa_uses_reported',
        on_delete=models.PROTECT
    )

    process_number = models.PositiveSmallIntegerField(null=True, blank=True)

    makeup_quantity = models.FloatField(
        validators=[MinValueValidator(0.0)],
        null=True,
        blank=True
    )

    emissions = models.FloatField(
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

    makeup_consumption = models.FloatField(validators=[MinValueValidator(0.0)])

    max_emissions = models.FloatField(validators=[MinValueValidator(0.0)])

    remark = models.CharField(max_length=9999, blank=True)

    class Meta:
        db_table = 'limit_pa_emission'
