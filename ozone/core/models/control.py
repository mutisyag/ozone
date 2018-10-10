from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .party import Party
from .reporting import ReportingPeriod
from .substance import Group


__all__ = [
    'ControlMeasure',
    'Limit',
    'ProcessAgentEmitLimit',
]


class ControlMeasure(models.Model):
    """
    Restrictions on level of production and consumption for Parties.
    """

    party = models.ForeignKey(
        Party, on_delete=models.PROTECT
    )

    group = models.ForeignKey(
        Group, on_delete=models.PROTECT
    )

    reporting_period = models.ForeignKey(
        ReportingPeriod, on_delete=models.PROTECT
    )

    production_allowed = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    consumption_allowed = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    basic_domestic_needs_allowed = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        blank=True, null=True
    )


class Limit(models.Model):
    """
    Production and Consumption Limits for Substances in a Group / Annex,
    for a Period, for a Party (EDT)
    """

    party = models.ForeignKey(
        Party, on_delete=models.PROTECT
    )
    reporting_period = models.ForeignKey(
        ReportingPeriod, on_delete=models.PROTECT
    )
    group = models.ForeignKey(
        Group, on_delete=models.PROTECT
    )

    production = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True

    )
    consumption = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    basic_domestic_needs_production = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )


class ProcessAgentEmitLimit(models.Model):
    """
    Emission limits for process agent uses, for non-Article 5 parties.
    """

    party = models.ForeignKey(
        Party, on_delete=models.PROTECT
    )

    decision = models.CharField(max_length=256)

    makeup_consumption = models.FloatField(validators=[MinValueValidator(0.0)])

    max_emissions = models.FloatField(validators=[MinValueValidator(0.0)])

    remark = models.CharField(max_length=512, blank=True)
