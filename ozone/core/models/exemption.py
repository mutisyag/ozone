from django.core.validators import MinValueValidator
from django.db import models

from .data import EssentialCriticalType
from .party import Party
from .reporting import Submission
from .substance import Substance


__all__ = [
    'Nomination',
    'ExemptionApproved',
]


class BaseExemption(models.Model):

    submission = models.ForeignKey(
        Submission, related_name='%(class)ss', on_delete=models.PROTECT
    )

    substance = models.ForeignKey(Substance, on_delete=models.PROTECT)

    quantity = models.FloatField(
        validators=[MinValueValidator(0.0)],
        blank=True, null=True
    )

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

    decision_approved = models.CharField(max_length=256, blank=True)

    approved_teap_amount = models.FloatField(
        validators=[MinValueValidator(0.0)],
        blank=True, null=True
    )

    essen_crit_type = models.ForeignKey(
        EssentialCriticalType,
        default=1,
        on_delete=models.PROTECT
    )

    class Meta:
        db_table = 'exemption_approved'
