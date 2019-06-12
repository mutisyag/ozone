from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .aggregation import ProdCons, ProdConsMT
from .legal import ReportingPeriod
from .party import Party
from .reporting import Submission, FormTypes
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

    transferred_amount = models.FloatField(validators=[MinValueValidator(0.0)])

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

    def get_aggregation_classes(self):
        potential = 1
        if self.substance.group.is_gwp:
            potential = self.substance.gwp
        elif self.substance.group.is_odp:
            potential = self.substance.odp

        data = [
            (
                ProdCons,
                {
                    'party': self.source_party,
                    'reporting_period': self.reporting_period,
                    'group': self.substance.group,
                },
                potential
            ),
            (
                ProdConsMT,
                {
                    'party': self.source_party,
                    'reporting_period': self.reporting_period,
                    'substance': self.substance,
                },
                1
            )
        ]
        return list(data)

    def populate_aggregated_data(self):
        """
        Populates relevant fields in aggregation tables based on this transfer.
        """
        for klass, params, potential in self.get_aggregation_classes():
            # Populate aggregation data
            aggregation, created = klass.objects.get_or_create(**params)
            if self.transfer_type == 'P':
                aggregation.prod_transfer += self.transferred_amount * potential
            elif self.transfer_type == 'C':
                aggregation.cons_transfer += self.transferred_amount * potential

            # Populate submissions list
            form_type = FormTypes.TRANSFER.value
            if form_type in aggregation.submissions:
                submissions_set = set(aggregation.submissions[form_type])
            else:
                submissions_set = set()
            if self.source_party_submission:
                submissions_set.add(self.source_party_submission.id)
            if self.destination_party_submission:
                submissions_set.add(self.destination_party_submission.id)
            aggregation.submissions[form_type] = list(submissions_set)

            aggregation.save()

    def clear_aggregated_data(self):
        for klass, params, potential in self.get_aggregation_classes():
            aggregation = klass.objects.filter(**params).first()
            if aggregation:
                # Delete the transfer data from the aggregation
                if self.transfer_type == 'P':
                    aggregation.prod_transfer -= self.transferred_amount * potential
                elif self.transfer_type == 'C':
                    aggregation.cons_transfer -= self.transferred_amount * potential
                aggregation.save()

                # Clear submissions from list
                form_type = FormTypes.TRANSFER.value
                if form_type in aggregation.submissions:
                    submissions_set = set(aggregation.submissions[form_type])
                else:
                    submissions_set = set()
                if (
                    self.source_party_submission
                    and self.source_party_submission.id in submissions_set
                ):
                    submissions_set.remove(self.source_party_submission.id)
                if (
                    self.destination_party_submission
                    and self.destination_party_submission.id in submissions_set
                ):
                    submissions_set.remove(self.destination_party_submission.id)
                aggregation.submissions[form_type] = list(submissions_set)

                # Delete empty aggregations
                if aggregation.is_empty():
                    aggregation.delete()

    def clean(self):
        if self.destination_party_submission:
            if self.destination_party_submission.party != self.destination_party:
                raise ValidationError(
                    {
                        'destination_party_submission': [_(
                            "Destination party submission should belong to the "
                            "transfer's destination party."
                        )],
                    }
                )
            if self.destination_party_submission.obligation.form_type != FormTypes.TRANSFER.value:
                raise ValidationError(
                    {
                        'destination_party_submission': [_(
                            "Destination party submission should be a Transfer "
                            "submission."
                        )],
                    }
                )

        if self.source_party_submission:
            if self.source_party_submission.party != self.source_party:
                raise ValidationError(
                    {
                        'source_party_submission': [_(
                            "Source party submission should belong to the "
                            "transfer's source party"
                        )],
                    }
                )
            if self.source_party_submission.obligation.form_type != FormTypes.TRANSFER.value:
                raise ValidationError(
                    {
                        'source_party_submission': [_(
                            "Source party submission should be a Transfer "
                            "submission."
                        )],
                    }
                )

        super().clean()

    def delete(self, *args, **kwargs):
        self.clear_aggregated_data()

        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()

        # Populate aggregation data
        self.populate_aggregated_data()

        super().save(*args, **kwargs)

    class Meta:
        db_table = 'reporting_transfer'
