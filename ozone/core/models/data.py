import datetime

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from model_utils import FieldTracker

from .legal import ReportingPeriod
from .party import Party, PartyRatification
from .reporting import ModifyPreventionMixin, Submission
from .substance import BlendComponent, Substance, Blend, Annex, Group
from .utils import model_to_dict

__all__ = [
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
    'DataOther',
]


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
                _("Substance rows derived from blends cannot be changed!")
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

            # Then recreate, skipping over substance-less components
            components = BlendComponent.objects.filter(
                blend=self.blend, substance__isnull=False
            )
            for component in components:
                # Init & populate kwargs for each blend component's save()
                field_dictionary = dict()
                for field in self.QUANTITY_FIELDS:
                    # Compute individual substance quantities
                    quantity = getattr(self, field)
                    field_dictionary[field] = component.percentage * quantity \
                        if quantity else None

                attributes = model_to_dict(
                    self,
                    exclude=[
                        'id', 'substance_id', 'blend_id', 'blend_item_id',
                        '_state', '_deferred_fields', '_tracker', 'save',
                    ],
                )
                attributes['substance_id'] = component.substance.pk
                attributes['blend_item_id'] = self.pk
                self.__class__.objects.create(**attributes)


class PolyolsMixin:
    def clean(self):
        if (not self.substance or not self.substance.is_contained_in_polyols) \
                and self.quantity_polyols:
            raise ValidationError(
                _("Cannot report polyols quantity if substance not in polyols!")
            )
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class BaseReport(models.Model):
    """
    This will be used as a base for all reporting models.
    """

    # We want to avoid deletion of `Submission`s which contain data reports.
    # In order to delete a non-submitted submission, its associated reports
    # will need to be deleted first.
    submission = models.ForeignKey(
        Submission, related_name='%(class)ss', on_delete=models.PROTECT
    )

    # Each entry in the Article 7 forms can have remarks
    remarks_party = models.CharField(max_length=9999, blank=True,
                                     help_text="Remarks added by the reporting party")
    remarks_os = models.CharField(max_length=9999, blank=True,
                                  help_text="Remarks added by the ozone secretariat")

    ordering_id = models.IntegerField(
        default=0,
        help_text="This allows the interface to keep the data entries in their original "
                  "order, as given by the user."
    )

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
        Substance, blank=True, null=True, on_delete=models.PROTECT,
        help_text="Substance ID"
    )
    blend = models.ForeignKey(
        Blend, blank=True, null=True, on_delete=models.PROTECT,
        help_text="Blend ID"
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

    quantity_polyols = models.FloatField(
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

    quantity_other_uses = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    decision_other_uses = models.CharField(
        max_length=256, blank=True
    )

    class Meta:
        abstract = True


class Article7Questionnaire(ModifyPreventionMixin, models.Model):
    """
    Model for a simple Article 7 Questionnaire report row
    """
    # There can be only one questionnaire per submission
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

    remarks_party = models.CharField(max_length=9999, blank=True)
    remarks_os = models.CharField(max_length=9999, blank=True)

    tracker = FieldTracker()

    class Meta:
        db_table = 'reporting_article_seven_questionnaire'


class Article7Export(
    ModifyPreventionMixin, PolyolsMixin, BaseBlendCompositionReport,
    BaseImportExportReport, BaseUses
):
    """
    Model for a simple Article 7 data report on exports.

    All quantities expressed in metric tonnes.
    """

    # Quantity fields needed for blend-to-substance breakdown
    # quantity_polyols is intentionally not included.
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
        'quantity_other_uses',
    ]

    # FieldTracker does not work on abstract models
    tracker = FieldTracker()

    destination_party = models.ForeignKey(
        Party,
        null=True,
        blank=True,
        related_name='article7exports_to',
        on_delete=models.PROTECT
    )

    class Meta:
        db_table = 'reporting_article_seven_exports'


class Article7Import(
    ModifyPreventionMixin, PolyolsMixin, BaseBlendCompositionReport,
    BaseImportExportReport, BaseUses
):
    """
    Model for a simple Article 7 data report on imports.

    All quantities expressed in metric tonnes.
    """

    # Quantity fields needed for blend-to-substance breakdown
    # quantity_polyols is intentionally not included.
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
        'quantity_other_uses',
    ]

    # FieldTracker does not work on abstract models
    tracker = FieldTracker()

    source_party = models.ForeignKey(
        Party,
        null=True,
        blank=True,
        related_name='article7imports_from',
        on_delete=models.PROTECT
    )

    class Meta:
        db_table = 'reporting_article_seven_imports'


class Article7Production(ModifyPreventionMixin, BaseReport, BaseUses):
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
    quantity_for_destruction = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    # "Production for supply to Article 5 countries in accordance
    # with Articles 2A‑2H and 5"
    quantity_article_5 = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )

    tracker = FieldTracker()

    class Meta:
        db_table = 'reporting_article_seven_production'


class Article7Destruction(ModifyPreventionMixin, BaseBlendCompositionReport):
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
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )

    class Meta:
        db_table = 'reporting_article_seven_destruction'


class Article7NonPartyTrade(ModifyPreventionMixin, BaseBlendCompositionReport):
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

    trade_party = models.ForeignKey(Party, blank=True, null=True, on_delete=models.PROTECT)

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

    @staticmethod
    def get_non_parties(group_pk, reporting_period_pk=None):
        """
        Returns qs of Parties for which the group identified by group_pk
        is not a controlled group of substances (i.e. Party had not ratified
        the Treaty that defines the Group as controlled at the date on which
        the given reporting period started).
        """
        group = Group.objects.get(pk=group_pk)
        if not reporting_period_pk:
            max_date = datetime.date.today()
        else:
            max_date = ReportingPeriod.objects.get(
                pk=reporting_period_pk
            ).start_date

        # Get all the Parties that had ratified the control treaty at that date
        current_ratifications = PartyRatification.objects.filter(
            entry_into_force_date__lte=max_date,
            treaty=group.control_treaty
        )
        signing_party_ids = set(
            current_ratifications.values_list('party__id', flat=True)
        )

        return Party.objects.exclude(
            Q(id__in=signing_party_ids) | Q(parent_party__id__in=signing_party_ids)
        )

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
                        "At least one quantity field should be non-null."
                    )]
                }
            )
        # If it's a blend we skip the validation because we will check every
        # component substance particularly.
        if not self.blend and self.substance and self.trade_party:
            non_parties = self.get_non_parties(self.substance.group_id)
            if self.trade_party not in non_parties:
                raise ValidationError(
                    {
                        'trade_party': [_(
                            "You need to select a non-party, according to the "
                            "selected substance."
                        )]
                    }
                )

        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Article7Emission(ModifyPreventionMixin, BaseReport):
    """
    Model for a simple Article 7 data report on HFC-23 emissions.

    All quantities expressed in metric tonnes.
    """

    facility_name = models.CharField(max_length=256)

    # Total amount generated
    quantity_generated = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    # Amount generated and captured for all uses
    quantity_captured_all_uses = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    # Amount generated and captured for feedstock use in your country
    quantity_captured_feedstock = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    # Amount generated and captured for destruction
    quantity_captured_for_destruction = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    # Amount used for feedstock without prior capture
    quantity_feedstock = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    # Amount destroyed without prior capture
    quantity_destroyed = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    # Amount of generated emissions
    quantity_emitted = models.FloatField(
        validators=[MinValueValidator(0.0)]
    )

    tracker = FieldTracker()

    class Meta:
        db_table = 'reporting_article_seven_emissions'


class BaseHighAmbientTemperature(models.Model):

    quantity_msac = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True,
        help_text="Used in multi-split air conditioners"
    )
    quantity_sdac = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True,
        help_text="Used in split ducted air conditioners"
    )
    quantity_dcpac = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True,
        help_text="Used in ducted commercial packaged air conditioners",
    )

    class Meta:
        abstract = True


class HighAmbientTemperatureProduction(
    ModifyPreventionMixin, BaseReport, BaseHighAmbientTemperature
):
    """
    Production under the exemption for high-ambient-temperature parties
    """
    substance = models.ForeignKey(
        Substance, on_delete=models.PROTECT
    )

    tracker = FieldTracker()


class HighAmbientTemperatureImport(
    ModifyPreventionMixin, BaseBlendCompositionReport,
    BaseHighAmbientTemperature
):
    """
    Consumption (imports) under the exemption for high-ambient-temperature
    parties
    """

    # Needed because of BaseBlendCompositionReport
    tracker = FieldTracker()

    # Needed because of BaseBlendCompositionReport
    QUANTITY_FIELDS = [
        'quantity_msac',
        'quantity_sdac',
        'quantity_dcpac',
    ]


class Transfer(ModifyPreventionMixin, BaseReport):
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

    tracker = FieldTracker()


class DataOther(ModifyPreventionMixin, BaseReport):
    """
    Model for Data Other reports.
    """

    tracker = FieldTracker()
