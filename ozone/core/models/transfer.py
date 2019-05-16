from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .aggregation import ProdCons, ProdConsMT
from .legal import ReportingPeriod
from .party import Party
from .reporting import Submission
from .substance import Substance


__all__ = [
    'Transfer',
]


class Transfer(models.Model):
    """
    Records amounts of production rights transferred between Parties.
    """
    TRANSFER_TYPE = (
        ('P', 'Production'),
        ('C', 'Consumption')
    )
    transfer_type = models.CharField(
        max_length=1,
        choices=TRANSFER_TYPE
    )

    source_party = models.ForeignKey(
        Party, related_name='sent_transfers', on_delete=models.PROTECT
    )

    destination_party = models.ForeignKey(
        Party, related_name='received_transfers', on_delete=models.PROTECT
    )

    reporting_period = models.ForeignKey(
        ReportingPeriod, related_name='transfers', on_delete=models.PROTECT
    )

    substance = models.ForeignKey(
        Substance, on_delete=models.PROTECT
    )

    transferred_amount = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )

    is_basic_domestic_need = models.BooleanField(default=False)

    # Related submissions.
    # This is the submission recorded by the source side
    source_party_submission = models.ForeignKey(
        Submission,
        blank=True,
        null=True,
        related_name='transfers_from',
        on_delete=models.PROTECT,
    )
    # This is the submission recorded by the destination side
    destination_party_submission = models.ForeignKey(
        Submission,
        blank=True,
        null=True,
        related_name='transfers_to',
        on_delete=models.PROTECT,
    )

    def populate_aggregated_data(self):
        """
        Populates relevant fields in aggregation tables based on this transfer.
        """
        if self.substance.group.is_gwp:
            potential = self.substance.gwp
        elif self.substance.group.is_odp:
            potential = self.substance.odp

        prod_cons, created = ProdCons.objects.get_or_create(
            party=self.source_party,
            reporting_period=self.reporting_period,
            group=self.substance.group,
        )
        if self.transfer_type == 'Production':
            prod_cons.prod_transfer += self.transferred_amount * potential
        else:
            prod_cons.cons_transfer += self.transferred_amount * potential
        prod_cons.save()

        prod_cons_mt, created = ProdConsMT.objects.get_or_create(
            party=self.source_party,
            reporting_period=self.reporting_period,
            substance=self.substance
        )
        if self.transfer_type == 'Production':
            prod_cons_mt.prod_transfer += self.transferred_amount
        else:
            prod_cons_mt.cons_transfer += self.transferred_amount
        prod_cons_mt.save()

    def clear_aggregated_data(self):
        prod_cons = ProdCons.objects.filter(
            party=self.source_party,
            reporting_period=self.reporting_period,
            group=self.substance.group
        ).first()
        if prod_cons:
            # Next line may be naive, what if we have 2 registered transfers
            # in the same reporting period?
            if self.transfer_type == 'Production':
                prod_cons.prod_transfer = 0.0
            else:
                prod_cons.cons_transfer = 0.0
            prod_cons.save()
            if prod_cons.is_empty():
                prod_cons.delete()

        prod_cons = ProdConsMT.objects.filter(
            party=self.source_party,
            reporting_period=self.reporting_period,
            substance=self.substance
        ).first()
        if prod_cons:
            # Next line may be naive, what if we have 2 registered transfers
            # in the same reporting period?
            if self.transfer_type == 'Production':
                prod_cons.prod_transfer = 0.0
            else:
                prod_cons.cons_transfer = 0.0
            prod_cons.save()
            if prod_cons.is_empty():
                prod_cons.delete()

    def clean(self):
        if (
            self.destination_party_submission and
            self.destination_party_submission.party != self.destination_party
        ):
            raise ValidationError(
                {
                    'destination_party_submission': [_(
                        "Destination party submission should belong to the "
                        "transfer's destination party"
                    )],
                }
            )
        if (
            self.source_party_submission and
            self.source_party_submission.party != self.source_party
        ):
            raise ValidationError(
                {
                    'source_party_submission': [_(
                        "Source party submission should belong to the "
                        "transfer's source party"
                    )],
                }
            )
        super().clean()

    def delete(self, *args, **kwargs):
        self.clear_aggregated_data()

        super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()

        # Populate aggregation data
        self.populate_aggregated_data()

        super().save(*args, **kwargs)

    class Meta:
        db_table = 'reporting_transfer'
