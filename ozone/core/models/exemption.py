from django.core.validators import MinValueValidator
from django.db import models

from .party import Party
from .reporting import Submission
from .substance import Substance


__all__ = [
    'Nomination',
    'ExemptionApproved',
    'ExemptionReported',
]


class BaseExemption(models.Model):

    submission = models.ForeignKey(
        Submission, related_name='%(class)ss', on_delete=models.PROTECT
    )

    substance = models.ForeignKey(Substance, on_delete=models.PROTECT)

    quantity = models.FloatField(validators=[MinValueValidator(0.0)])

    remarks_os = models.CharField(
        max_length=9999, blank=True,
        help_text="Remarks added by the ozone secretariat"
    )

    ordering_id = models.IntegerField(
        default=0,
        help_text="This allows the interface to keep the data entries in their"
                  "original order, as given by the user."
    )

    class Meta:
        abstract = True


class Nomination(BaseExemption):
    """
    Filled by a Secretariat based on an attachment uploaded by a Party.
    """

    class Meta:
        db_table = 'exemption_nomination'


class ExemptionApproved(BaseExemption):
    """
    Filled by a Secretariat after a Meeting of the Parties (or an emergency decision).
    """

    emergency = models.BooleanField(default=False)

    decision_approved = models.CharField(max_length=256, blank=True)

    class Meta:
        db_table = 'exemption_approved'


class ExemptionReported(models.Model):

    substance = models.ForeignKey(
        Substance, on_delete=models.PROTECT
    )

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

    remark = models.CharField(max_length=256, blank=True)

    class Meta:
        db_table = 'exemption_reported'
