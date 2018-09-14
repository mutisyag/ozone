import enum

from django.core.validators import MinValueValidator
from django.db import models

from .meeting import Decision
from .reporting import Submission
from .substance import Annex, Group, Substance, Blend
from .party import Party

__all__ = [
    'Article7Flags',
    'Article7Questionnaire',
    'Article7Export',
    'Article7Import',
    'Article7Production',
    'Article7Destruction',
    'Article7NonPartyTrade',
    'Article7Emission',
]

@enum.unique
class ExemptionTypes(enum.Enum):
    """
    General enum of ratification types; should be useful in other models too
    """
    CRITICAL = 'Critical use'
    ESSENTIAL = 'Essential use'
    HIGH_AMBIENT = 'High ambient'
    PROCESS_AGENT = 'Process agent'
    LABORATORY = 'Laboratory'       # TODO: not sure this should be here
    OTHER = 'Other'


class BaseDataReport(models.Model):
    """
    This will be used as a base for all reporting models.
    """

    # Django syntax for generating proper related_name in concrete model
    submission = models.ForeignKey(
        Submission, related_name='%(class)ss', on_delete=models.PROTECT
    )

    # TODO: ensure in save() that one and only one of these two
    # is non-null
    substance = models.ForeignKey(
        Substance, null=True, on_delete=models.PROTECT
    )
    blend = models.ForeignKey(
        Blend, null=True, on_delete=models.PROTECT
    )

    # Each entry in the Article 7 forms can have remarks
    remarks_party = models.CharField(max_length=512, blank=True)
    remarks_os = models.CharField(max_length=512, blank=True)

    class Meta:
        abstract = True


class Article7Flags(models.Model):
    """
    Stores incomplete flags per submission-annex-group.

    Only needs to be instantiated when there is incomplete data.
    """

    submission = models.ForeignKey(
        Submission, related_name='incomplete_flags', on_delete=models.PROTECT
    )

    annex = models.ForeignKey(
        Annex, related_name='incomplete_flags', on_delete=models.PROTECT
    )
    group = models.ForeignKey(
        Group, related_name='incomplete_flags', on_delete=models.PROTECT
    )

    # Generally this model will be instantiated only when there is incomplete
    # data in the submission
    flag_incomplete = models.BooleanField(default=True)

    class Meta:
        db_table = 'reporting_article_seven_flags'


class Article7Questionnaire(BaseDataReport):
    """
    Model for a simple Article 7 Questionnaire report row
    """
    # TODO: this really should not inherit BaseDataReport

    has_imports = models.BooleanField()

    has_exports = models.BooleanField()

    has_produced = models.BooleanField()

    has_destroyed = models.BooleanField()

    has_nonparty = models.BooleanField()

    has_emissions = models.BooleanField()

    class Meta:
        db_table = 'reporting_article_seven_questionnaire'


class Article7Export(BaseDataReport):
    """
    Model for a simple Article 7 data report on exports.

    All quantities expressed in metric tonnes.
    """

    quantity_total_new = models.FloatField(
        validators=[MinValueValidator(0.0)], null=True
    )
    quantity_total_recovered = models.FloatField(
        validators=[MinValueValidator(0.0)], null=True
    )
    quantity_feedstock = models.FloatField(
        validators=[MinValueValidator(0.0)], null=True
    )

    # Exemption quantity w/ type & decision
    # TODO: should maybe ensure that type & decision are not null if
    # quantity is not null
    # TODO: mixin for this and other common stuff
    quantity_exempted = models.FloatField(
        validators=[MinValueValidator(0.0)], null=True
    )
    type_exempted = models.CharField(
        max_length=32,
        choices=((e.value, e.name) for e in ExemptionTypes),
        blank=True
    )
    decision = models.ForeignKey(
        Decision, null=True, on_delete=models.PROTECT
    )

    class Meta:
        db_table = 'reporting_article_seven_exports'


class Article7Import(BaseDataReport):
    """
    Model for a simple Article 7 data report on imports.

    All quantities expressed in metric tonnes.
    """

    quantity_total_new = models.FloatField(
        validators=[MinValueValidator(0.0)], null=True
    )
    quantity_total_recovered = models.FloatField(
        validators=[MinValueValidator(0.0)], null=True
    )
    quantity_feedstock = models.FloatField(
        validators=[MinValueValidator(0.0)], null=True
    )

    # Exemption quantity w/ type & decision
    quantity_exempted = models.FloatField(
        validators=[MinValueValidator(0.0)], null=True
    )
    type_exempted = models.CharField(
        max_length=32,
        choices=((e.value, e.name) for e in ExemptionTypes),
        blank=True
    )
    decision = models.ForeignKey(
        Decision, null=True, on_delete=models.PROTECT
    )

    class Meta:
        db_table = 'reporting_article_seven_imports'


class Article7Production(BaseDataReport):
    """
    Model for a simple Article 7 data report on production.

    All quantities expressed in metric tonnes.
    """

    quantity_total_produced = models.FloatField(
        validators=[MinValueValidator(0.0)], null=True
    )
    quantity_feedstock = models.FloatField(
        validators=[MinValueValidator(0.0)], null=True
    )
    # TODO: ensure in save() that this is reported only for annex C group I.
    # "Production for supply to Article 5 countries in accordance
    # with Articles 2A‑2H and 5"
    quantity_article_5 = models.FloatField(
        validators=[MinValueValidator(0.0)], null=True
    )

    # Exemption quantity w/ type & decision
    quantity_exempted = models.FloatField(
        validators=[MinValueValidator(0.0)], null=True
    )
    type_exempted = models.CharField(
        max_length=32,
        choices=((e.value, e.name) for e in ExemptionTypes),
        blank=True
    )
    decision = models.ForeignKey(
        Decision, null=True, on_delete=models.PROTECT
    )

    class Meta:
        db_table = 'reporting_article_seven_production'


class Article7Destruction(BaseDataReport):
    """
    Model for a simple Article 7 data report on destruction.

    All quantities expressed in metric tonnes.
    """

    quantity_destroyed = models.FloatField(
        validators=[MinValueValidator(0.0)]
    )

    class Meta:
        db_table = 'reporting_article_seven_destruction'


class Article7NonPartyTrade(BaseDataReport):
    """
    Model for a simple Article 7 data report on non-party trade.

    All quantities expressed in metric tonnes.
    """

    trade_party = models.ForeignKey(Party, on_delete=models.PROTECT)

    # TODO: save() - ensure at least one of these quantity fields is non-null
    quantity_import_new = models.FloatField(
        validators=[MinValueValidator(0.0)], null=True
    )
    quantity_import_recovered = models.FloatField(
        validators=[MinValueValidator(0.0)], null=True
    )
    quantity_export_new = models.FloatField(
        validators=[MinValueValidator(0.0)], null=True
    )
    quantity_export_recovered = models.FloatField(
        validators=[MinValueValidator(0.0)], null=True
    )

    class Meta:
        db_table = 'reporting_article_seven_non_party_trade'


class Article7Emission(models.Model):
    """
    Model for a simple Article 7 data report on HFC-23 emissions.

    All quantities expressed in metric tonnes.
    """

    # related_name respecting the convention for all other models here.
    submission = models.ForeignKey(
        Submission,
        related_name='article7emissions',
        on_delete=models.PROTECT
    )

    facility_name = models.CharField(max_length=256)

    quantity_emitted = models.FloatField(
        validators=[MinValueValidator(0.0)]
    )

    remarks_party = models.CharField(max_length=512, blank=True)
    remarks_os = models.CharField(max_length=512, blank=True)

    class Meta:
        db_table = 'reporting_article_seven_emissions'
