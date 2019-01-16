from django.core.validators import MinValueValidator
from django.db import models

from .party import Party
from .reporting import ReportingPeriod
from .substance import Substance, UsesType


__all__ = [
    'Nomination',
    'ExemptionApproved',
    'ExemptionReported',
]


class Nomination(models.Model):
    """
    Submitted by a Party for an Exemption.
    """

    nomination_id = models.CharField(max_length=16, unique=True)

    party = models.ForeignKey(
        Party, related_name='nominations', on_delete=models.PROTECT
    )

    reporting_period = models.ForeignKey(
        ReportingPeriod, related_name='nominations', on_delete=models.PROTECT
    )

    uses_type = models.ForeignKey(
        UsesType, related_name='nominations', on_delete=models.PROTECT
    )

    substance = models.ForeignKey(Substance, on_delete=models.PROTECT)

    submit_date = models.DateField()

    submit_amount = models.FloatField(validators=[MinValueValidator(0.0)])

    remark = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return self.nomination_id

    class Meta:
        ordering = ('nomination_id',)
        db_table = 'exemption_nomination'


class BaseExemption(models.Model):

    party = models.ForeignKey(
        Party, related_name='%(class)ss', on_delete=models.PROTECT
    )

    reporting_period = models.ForeignKey(
        ReportingPeriod, on_delete=models.PROTECT
    )

    substance = models.ForeignKey(
        Substance, on_delete=models.PROTECT
    )

    uses_type = models.ForeignKey(
        UsesType, on_delete=models.PROTECT
    )

    critical_uses_category = models.CharField(max_length=256, blank=True)

    remark = models.CharField(max_length=256, blank=True)

    class Meta:
        abstract = True


class ExemptionApproved(BaseExemption):

    emergency = models.BooleanField(default=False)

    approved_teap_amount = models.FloatField(
        validators=[MinValueValidator(0.0)]
    )
    approved_amount = models.FloatField(
        validators=[MinValueValidator(0.0)]
    )
    decision_approved = models.CharField(max_length=256, blank=True)

    laboratory_analytical_uses_category = models.CharField(
        max_length=256, blank=True
    )

    class Meta:
        db_table = 'exemption_approved'


class ExemptionReported(BaseExemption):

    import_party = models.ForeignKey(
        Party, on_delete=models.PROTECT
    )

    quantity_exempted = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    quantity_produced = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    quantity_imported = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    # TODO: what is this?
    quantity_open_bal = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    quantity_essential_uses = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    quantity_exported = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    quantity_destroyed = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )

    class Meta:
        db_table = 'exemption_reported'
