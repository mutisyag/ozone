from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .legal import ReportingPeriod
from .meeting import Decision
from .party import Party
from .substance import Group
from .utils import DECIMAL_FIELD_DECIMALS, DECIMAL_FIELD_DIGITS


__all__ = [
    'PlanOfActionDecision',
    'PlanOfAction',
]


class PlanOfActionDecision(models.Model):
    """
    Implements the Plans_Of_Action_Decs table from the legacy data.
    """
    decision = models.ForeignKey(Decision, on_delete=models.PROTECT)

    party = models.ForeignKey(Party, on_delete=models.PROTECT)

    year_adopted = models.PositiveIntegerField()

    def __str__(self):
        return (
            f"Decision {self.decision} for {self.party} - {self.year_adopted}"
        )

    class Meta:
        db_table = 'plan_of_action_decision'
        ordering = ('-year_adopted', 'party__name')


class PlanOfAction(models.Model):
    """
    Implements the Plans_Of_Action table from the legacy data.
    """
    party = models.ForeignKey(
        Party, related_name='plans_of_action', on_delete=models.PROTECT
    )

    reporting_period = models.ForeignKey(
        ReportingPeriod,
        related_name='plans_of_action',
        on_delete=models.PROTECT
    )

    group = models.ForeignKey(
        Group, related_name='plans_of_action', on_delete=models.PROTECT
    )

    benchmark = models.DecimalField(
        max_digits=DECIMAL_FIELD_DIGITS, decimal_places=DECIMAL_FIELD_DECIMALS,
        default=0.0, validators=[MinValueValidator(0.0)]
    )

    annex_group_description = models.CharField(
        max_length=256, blank=True, verbose_name=_('annex group description')
    )

    combined_id = models.BooleanField(default=False)

    is_valid = models.BooleanField(default=True)

    decision = models.ForeignKey(
        PlanOfActionDecision,
        related_name='plans_of_action',
        on_delete=models.PROTECT
    )

    def __str__(self):
        return (
            f"Plan of Action for {self.party} - {self.reporting_period} - "
            f"{self.group}"
        )

    def clean(self):
        if self.party != self.decision.party:
            raise ValidationError(
                _('Plan of Action party is not the same as the decision party!')
            )
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'plan_of_action'
        verbose_name_plural = 'plans of action'
        unique_together = ('party', 'reporting_period', 'group', 'is_valid',)
        ordering = ('party__name', '-reporting_period', 'group',)
