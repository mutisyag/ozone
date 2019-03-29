import enum

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .party import Party, PartyType
from .reporting import ReportingPeriod
from .substance import Group


__all__ = [
    'BaselineType',
    'LimitTypes',
    'ControlMeasure',
    'Baseline',
    'Limit',
    'ProcessAgentEmissionLimit',
]


class BaselineType(models.Model):
    """
    Categories of baselines for production, consumption and BDN production.
    """

    name = models.CharField(
        max_length=64,
        help_text="Baseline types can be A5/NA5 Prod/Cons, BDN_pre2k or BDN"
    )
    remarks = models.CharField(
        max_length=9999, blank=True,
        help_text="Remarks for this baseline type"
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'baseline_type'


@enum.unique
class LimitTypes(enum.Enum):
    PRODUCTION = 'Production'
    CONSUMPTION = 'Consumption'
    BDN = 'BDN'


class ControlMeasure(models.Model):
    """
    Restrictions on level of production and consumption for Parties.
    """

    limit_type = models.CharField(
        max_length=64, choices=((s.value, s.name) for s in LimitTypes),
        help_text="Control measure types can be Production, Consumption and BDN"
    )

    group = models.ForeignKey(
        Group, related_name='control_measures', on_delete=models.PROTECT,
        help_text="Annex group"
    )

    party_type = models.ForeignKey(
        PartyType,
        related_name='control_measures',
        on_delete=models.PROTECT
    )

    baseline_type = models.ForeignKey(
        BaselineType, related_name='control_measures', on_delete=models.PROTECT,
        help_text="Baseline type: A5/NA5 Prod/Cons or BDN"
    )

    # this is always required, and can be in the future
    start_date = models.DateField()

    # This can be blank. When not present, it is valid until the end of time
    end_date = models.DateField(blank=True, null=True)

    allowed = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )

    class Meta:
        db_table = 'control_measure'


class Baseline(models.Model):
    """
    Baseline by party and annex group and type (Prod/Cons/BDN)
    """

    party = models.ForeignKey(
        Party, related_name='baselines', on_delete=models.PROTECT
    )
    group = models.ForeignKey(
        Group, related_name='baselines', on_delete=models.PROTECT
    )
    baseline_type = models.ForeignKey(
        BaselineType, related_name='baselines', on_delete=models.PROTECT,
        help_text="Baseline type: A5/NA5 Prod/Cons or BDN"
    )

    baseline = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )

    class Meta:
        db_table = 'baseline'


class Limit(models.Model):
    """
    Production and Consumption Limits for Substances in a Group / Annex,
    for a Period, for a Party (EDT)
    """

    party = models.ForeignKey(
        Party, related_name='limits', on_delete=models.PROTECT
    )
    reporting_period = models.ForeignKey(
        ReportingPeriod, related_name='limits', on_delete=models.PROTECT
    )
    group = models.ForeignKey(
        Group, related_name='limits', on_delete=models.PROTECT
    )

    limit_type = models.CharField(
        max_length=64, choices=((s.value, s.name) for s in LimitTypes),
        help_text="Limit types can be Production, Consumption and BDN"
    )

    limit = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )

    class Meta:
        db_table = 'limit'


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
        db_table = 'pa_emission_limit'
