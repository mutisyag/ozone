from django.core.validators import MinValueValidator
from django.db import models

from .party import Party
from .reporting import Submission
from .substance import Substance

__all__ = [
    'ProcessAgentContainTechnology',
    'ProcessAgentApplication',
    'ProcessAgentUsesReported',
    'ProcessAgentEmissionLimit',
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
        db_table = 'pa_contain_technology'


class ProcessAgentApplication(models.Model):
    """
    Applications of controlled substances as process agents, as approved
    in table A of decision X/14 and updated periodically by the Meeting of the
    Parties.
    """

    decision = models.CharField(max_length=256, blank=True)

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

    decision = models.CharField(max_length=256)

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
        db_table = 'pa_uses_reported'


class ProcessAgentEmissionLimit(models.Model):
    """
    Emission limits for process agent uses, for non-Article 5 parties.
    """

    party = models.ForeignKey(
        Party,
        related_name='process_agent_emission_limits',
        on_delete=models.PROTECT
    )

    decision = models.CharField(max_length=256)

    makeup_consumption = models.FloatField(validators=[MinValueValidator(0.0)])

    max_emissions = models.FloatField(validators=[MinValueValidator(0.0)])

    remark = models.CharField(max_length=9999, blank=True)

    class Meta:
        db_table = 'limit_pa_emission'
