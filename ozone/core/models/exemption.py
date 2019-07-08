import re

from django.core.validators import MinValueValidator
from django.db import models

from .reporting import Submission
from .substance import Substance


__all__ = [
    'Nomination',
    'ExemptionApproved',
    'CriticalUseCategory',
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

    is_emergency = models.BooleanField(default=False)

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

    @classmethod
    def get_approved_amounts(cls, party, reporting_period):
        approvals = cls.objects.prefetch_related(
            'submission__party', 'submission__reporting_period'
        ).filter(
            submission__party=party,
            submission__reporting_period=reporting_period,
        ).values_list('substance', 'quantity', 'is_emergency')

        ret = {'emergency': {}, 'non_emergency': {}}
        for substance, amount, emergency in approvals:
            if emergency:
                if substance in ret['emergency']:
                    ret['emergency'][substance] += amount if amount else 0
                else:
                    ret['emergency'][substance] = amount if amount else 0
            else:
                if substance in ret['non_emergency']:
                    ret['non_emergency'][substance] += amount if amount else 0
                else:
                    ret['non_emergency'][substance] = amount if amount else 0
        return ret

    class Meta:
        db_table = 'exemption_approved'


class CriticalUseCategory(models.Model):
    """
    Used when recording agreed and actual critical uses (exemptions) of MeBr
    """

    code = models.CharField(max_length=256, unique=True)
    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_alt_name(cls, name):
        # Used to cleanup values during import of legacy data
        return re.sub('[^A-Z]+', '', name.replace('&', 'AND').upper())

    class Meta:
        ordering = ('name',)
        db_table = 'critical_use_category'
        verbose_name_plural = 'critical use categories'


class ApprovedCriticalUse(models.Model):
    """
    Breakdown of Approved exempted amount per critical use category.
    """
    exemption = models.ForeignKey(
        ExemptionApproved,
        related_name='approved_uses',
        on_delete=models.PROTECT
    )

    critical_use_category = models.ForeignKey(
        CriticalUseCategory,
        related_name='approved_uses',
        on_delete=models.CASCADE
    )

    quantity = models.FloatField(
        validators=[MinValueValidator(0.0)],
        blank=True, null=True
    )

    class Meta:
        db_table = 'exemption_approved_critical_use'
