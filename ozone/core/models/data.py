from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from model_utils import FieldTracker

from .meeting import Decision, ExemptionTypes
from .party import Party
from .reporting import Submission
from .substance import BlendComponent, Substance, Blend, Annex, Group

__all__ = [
    'Article7Flags',
    'Article7Questionnaire',
    'Article7Export',
    'Article7Import',
    'Article7Production',
    'Article7Destruction',
    'Article7NonPartyTrade',
    'Article7Emission',
    'HighAmbientTemperatureProduction',
    'HighAmbientTemperatureImport',
    'Transfer',
]

# TODO: implement delete-prevention logic on data reports for submitted
# submissions. :)


class BlendCompositionMixin:
    """
    Mixin to be used by data report models that accept both substances
    and blends.

    Each model that uses it needs to have the proper `QUANTITY_FIELDS` attribute
    set, e.g.:
    QUANTITY_FIELDS = [
        'quantity_total_new',
        'quantity_total_recovered',
        'quantity_feedstock'
    ]
    Also, all models using it need a field tracker.

    In case a blend-based row is created, additional substance-based rows for
    each blend component will be created.

    NB: order of inheritance - this should come before models.Model!
    """

    def clean(self):
        """
        Overriding the clean() method to ensure that substances and blends are
        not both specified.

        This is called explicitly from the save() method, also overridden in
        this class.
        """
        if self.substance is None and self.blend is None:
            raise ValidationError(
                {
                    'substance': [_(
                        'Data should refer to one substance or one blend'
                    )],
                    'blend': [_(
                        'Data should refer to one substance or one blend'
                    )]
                }
            )
        if self.substance is not None and self.blend is not None:
            raise ValidationError(
                {
                    'substance': [_(
                        'Data should not refer to both a substance and a blend'
                    )],
                    'blend': [_(
                        'Data should not refer to both a substance and a blend'
                    )]
                }
            )

        # Also, no changes are allowed on blend_item != null objects
        if self.tracker.changed() and self.tracker.previous('blend_item_id'):
            raise ValidationError(
                _('Substance rows derived from blends cannot be changed!')
            )

        super().clean()

    def save(self, *args, **kwargs):
        """
        This overrides save() to also create rows for each substance (component)
        in a blend.
        """

        # Call clean() to perform either-substance-or-blend validation
        self.full_clean()

        super().save(*args, **kwargs)

        # If blend has changed, child rows should be deleted.
        # Tracker adds an '_id' to foreign key field names.
        if self.tracker.has_changed('blend_id'):
            changed_fields = self.QUANTITY_FIELDS
        else:
            # If any of the QUANTITY_FIELDS have changed for a blend,
            # child rows should be deleted.
            changed_fields = [field for field in self.QUANTITY_FIELDS
                              if self.tracker.has_changed(field)]
        if not changed_fields:
            return

        with transaction.atomic():
            # First delete all child rows (using related_name)
            self.components.all().delete()

            # Then recreate
            components = BlendComponent.objects.filter(blend=self.blend)
            for component in components:
                # Init & populate kwargs for each blend component's save()
                field_dictionary = dict()
                for field in self.QUANTITY_FIELDS:
                    # Compute individual substance quantities
                    quantity = getattr(self, field)
                    field_dictionary[field] = component.percentage * quantity \
                        if quantity else None

                # Now save the component substance row
                report = self.__class__.objects.create(
                    submission=self.submission,
                    substance=component.substance,
                    blend=None,
                    blend_item=self,
                    # Quantities for specific substance
                    **field_dictionary
                )
                report.save()


class BaseReport(models.Model):
    """
    This will be used as a base for all reporting models, except Article7Flags.
    """

    # Django syntax for generating proper related_name in concrete model
    submission = models.ForeignKey(
        Submission, related_name='%(class)ss', on_delete=models.CASCADE
    )

    # Each entry in the Article 7 forms can have remarks
    remarks_party = models.CharField(max_length=512, blank=True)
    remarks_os = models.CharField(max_length=512, blank=True)

    class Meta:
        abstract = True


class BaseBlendCompositionReport(BlendCompositionMixin, BaseReport):
    """
    This will be used as a base for all reporting models that accept
    both substances and blends.

    Since it uses the blend composition mixin, all models inheriting this
    need the following:
    - a FieldTracker called `tracker`
    - the proper `QUANTITY_FIELDS` attribute set, e.g.:
    QUANTITY_FIELDS = [
        'quantity_total_new',
        'quantity_total_recovered',
        'quantity_feedstock'
    ]

    """

    # `blank=True` is needed for full_clean() calls performed by save()
    substance = models.ForeignKey(
        Substance, blank=True, null=True, on_delete=models.PROTECT
    )
    blend = models.ForeignKey(
        Blend, blank=True, null=True, on_delete=models.PROTECT
    )
    # When non-null, this is used to signal that this particular
    # substance entry was automatically generated from an entry containing
    # a blend.
    blend_item = models.ForeignKey(
        'self',
        related_name='components',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True


class BaseImportExportReport(models.Model):
    """
    This will be used as a base for data reporting models on import and export.
    """

    quantity_total_new = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    quantity_total_recovered = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    quantity_feedstock = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )

    class Meta:
        abstract = True


class BaseUses(models.Model):
    """
    This will be used as a base for data reporting models on import, export
    and production.
    This model contains the quantities and the decisions to use controlled
    substances.
    """

    quantity_critical_uses = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    decision_critical_uses = models.CharField(max_length=256, blank=True)

    quantity_essential_uses = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    decision_essential_uses = models.CharField(max_length=256, blank=True)

    quantity_high_ambient_temperature = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    decision_high_ambient_temperature = models.CharField(
        max_length=256, blank=True
    )

    quantity_laboratory_analytical_uses = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    decision_laboratory_analytical_uses = models.CharField(
        max_length=256, blank=True
    )

    quantity_process_agent_uses = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    decision_process_agent_uses = models.CharField(max_length=256, blank=True)

    quantity_quarantine_pre_shipment = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    decision_quarantine_pre_shipment = models.CharField(
        max_length=256, blank=True
    )

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


class Article7Questionnaire(BaseReport):
    """
    Model for a simple Article 7 Questionnaire report row
    """
    # Overriding submission field; there can be only one questionnaire
    # per submission
    submission = models.OneToOneField(
        Submission,
        related_name='article7questionnaire',
        on_delete=models.CASCADE
    )

    has_imports = models.BooleanField()

    has_exports = models.BooleanField()

    has_produced = models.BooleanField()

    has_destroyed = models.BooleanField()

    has_nonparty = models.BooleanField()

    has_emissions = models.BooleanField()

    class Meta:
        db_table = 'reporting_article_seven_questionnaire'


class Article7Export(
    BaseBlendCompositionReport, BaseImportExportReport, BaseUses
):
    """
    Model for a simple Article 7 data report on exports.

    All quantities expressed in metric tonnes.
    """

    # Quantity fields needed for blend-to-substance breakdown
    QUANTITY_FIELDS = [
        'quantity_critical_uses',
        'quantity_essential_uses',
        'quantity_high_ambient_temperature',
        'quantity_laboratory_analytical_uses',
        'quantity_process_agent_uses',
        'quantity_quarantine_pre_shipment',
        'quantity_total_new',
        'quantity_total_recovered',
        'quantity_feedstock',
    ]

    # FieldTracker does not work on abstract models
    tracker = FieldTracker()

    class Meta:
        db_table = 'reporting_article_seven_exports'


class Article7Import(
    BaseBlendCompositionReport, BaseImportExportReport, BaseUses
):
    """
    Model for a simple Article 7 data report on imports.

    All quantities expressed in metric tonnes.
    """

    # Quantity fields needed for blend-to-substance breakdown
    QUANTITY_FIELDS = [
        'quantity_critical_uses',
        'quantity_essential_uses',
        'quantity_high_ambient_temperature',
        'quantity_laboratory_analytical_uses',
        'quantity_process_agent_uses',
        'quantity_quarantine_pre_shipment',
        'quantity_total_new',
        'quantity_total_recovered',
        'quantity_feedstock',
    ]

    # FieldTracker does not work on abstract models
    tracker = FieldTracker()

    class Meta:
        db_table = 'reporting_article_seven_imports'


class Article7Production(BaseReport, BaseUses):
    """
    Model for a simple Article 7 data report on production.

    All quantities expressed in metric tonnes.
    """

    substance = models.ForeignKey(Substance, on_delete=models.PROTECT)

    quantity_total_produced = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    quantity_feedstock = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    # TODO: ensure in save() that this is reported only for annex C group I.
    # "Production for supply to Article 5 countries in accordance
    # with Articles 2A‑2H and 5"
    quantity_article_5 = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )

    class Meta:
        db_table = 'reporting_article_seven_production'


class Article7Destruction(BaseBlendCompositionReport):
    """
    Model for a simple Article 7 data report on destruction.

    All quantities expressed in metric tonnes.
    """

    # Needed by the BlendCompositionMixin
    tracker = FieldTracker()

    QUANTITY_FIELDS = [
        'quantity_destroyed',
    ]

    quantity_destroyed = models.FloatField(
        validators=[MinValueValidator(0.0)]
    )

    class Meta:
        db_table = 'reporting_article_seven_destruction'


class Article7NonPartyTrade(BaseBlendCompositionReport):
    """
    Model for a simple Article 7 data report on non-party trade.

    All quantities expressed in metric tonnes.
    """

    tracker = FieldTracker()

    QUANTITY_FIELDS = [
        'quantity_import_new',
        'quantity_import_recovered',
        'quantity_export_new',
        'quantity_export_recovered',
    ]

    trade_party = models.ForeignKey(Party, on_delete=models.PROTECT)

    quantity_import_new = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    quantity_import_recovered = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    quantity_export_new = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    quantity_export_recovered = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )

    class Meta:
        db_table = 'reporting_article_seven_non_party_trade'

    def clean(self):
        if not (
            self.quantity_import_new
            or self.quantity_import_recovered
            or self.quantity_export_new
            or self.quantity_export_recovered
        ):
            raise ValidationError(
                {
                    'quantity_fields': [_(
                        'At least one quantity field should be non-null!'
                    )]
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Article7Emission(BaseReport):
    """
    Model for a simple Article 7 data report on HFC-23 emissions.

    All quantities expressed in metric tonnes.
    """

    facility_name = models.CharField(max_length=256)

    quantity_generated = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    quantity_feedstock = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    quantity_destroyed = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    quantity_emitted = models.FloatField(
        validators=[MinValueValidator(0.0)]
    )

    class Meta:
        db_table = 'reporting_article_seven_emissions'


class BaseHighAmbientTemperature(models.Model):

    # Multi-split air conditioners
    quantity_msac_produced = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    # Split ducted air conditioners
    quantity_sdac_produced = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    # Ducted commercial packaged air conditioners
    quantity_dcpac_produced = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )

    class Meta:
        abstract = True


class HighAmbientTemperatureProduction(BaseReport, BaseHighAmbientTemperature):
    """
    Production under the exemption for high-ambient-temperature parties
    """
    substance = models.ForeignKey(
        Substance, on_delete=models.PROTECT
    )


class HighAmbientTemperatureImport(
    BaseBlendCompositionReport, BaseHighAmbientTemperature
):
    """
    Consumption (imports) under the exemption for high-ambient-temperature
    parties
    """

    # Needed because of BaseBlendCompositionReport
    tracker = FieldTracker()

    # Needed because of BaseBlendCompositionReport
    QUANTITY_FIELDS = [
        'quantity_msac_produced',
        'quantity_sdac_produced',
        'quantity_dcpac_produced',
    ]


class Transfer(BaseReport):
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

    substance = models.ForeignKey(
        Substance, on_delete=models.PROTECT
    )

    transferred_amount = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    used_amount = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )

    is_basic_domestic_need = models.BooleanField(default=False)

    destination_party = models.ForeignKey(
        Party, related_name='received_transfers', on_delete=models.PROTECT
    )
