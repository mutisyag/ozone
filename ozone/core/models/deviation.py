import enum

from django.core.validators import MinValueValidator
from django.db import models

from .legal import ReportingPeriod
from .party import Party
from .substance import Group


__all__ = [
    'DeviationType',
    'DeviationSource',
]


@enum.unique
class DeviationPCTypes(enum.Enum):
    A = 'A'
    P = 'P'
    C = 'C'


class DeviationType(models.Model):
    """
    Implements the DeviationTypes legacy table.
    """
    deviation_type_id = models.CharField(max_length=256, unique=True)

    description = models.CharField(max_length=256, blank=True)

    deviation_pc = models.CharField(
        max_length=16, choices=((p.value, p.name) for p in DeviationPCTypes)
    )

    remark = models.CharField(max_length=512, blank=True)

    def __str__(self):
        return self.deviation_type_id

    class Meta:
        db_table = 'deviation_type'


class DeviationSource(models.Model):
    """
    Implements the DeviationSources legacy table.
    """
    party = models.ForeignKey(
        Party, related_name='deviation_sources', on_delete=models.PROTECT
    )

    reporting_period = models.ForeignKey(
        ReportingPeriod,
        related_name='deviation_sources',
        on_delete=models.PROTECT
    )

    group = models.ForeignKey(
        Group, related_name='deviation_sources', on_delete=models.PROTECT
    )

    deviation_type = models.ForeignKey(
        DeviationType,
        related_name='deviation_sources',
        on_delete=models.PROTECT
    )

    production = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )

    consumption = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )

    remark = models.CharField(max_length=512, blank=True)

    def __str__(self):
        return (
            f"Deviation source for {self.party.name} - "
            f"{self.reporting_period.name} - {self.group}, of type "
            f"{self.deviation_type}"
        )

    class Meta:
        # TODO: should this be 'reporting_deviation_source'?
        db_table = 'deviation_source'
        unique_together = (
            'party', 'reporting_period', 'group', 'deviation_type'
        )
