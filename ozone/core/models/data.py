from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from model_utils import FieldTracker

from .exemption import CriticalUseCategory
from .party import Party
from .reporting import ModifyPreventionMixin, Submission
from .substance import BlendComponent, Substance, Blend
from .aggregation import ProdCons, ProdConsMT
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
    'DataOther',
    'RAFReport',
    'RAFReportUseCategory',
    'RAFImport',
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

        # If this is a custom blend from a different party, raise an error
        if (
            self.blend is not None
            and self.blend.party is not None
            and self.blend.party != self.submission.party
        ):
            raise ValidationError(
                _("This blend is for a different party!")
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


class AggregationMixin:
    """
    Used by all data-report classes that need to generate aggregated data.
    """

    @classmethod
    def get_fields_sum_by_group(cls, submission, group, field_names):
        """
        Returns sum of quantities reported for given group_id, for a certain
        submission. Quantities are multiplied by either the ODP or GWP of each
        substance.
        """
        def zero_if_none(value):
            return Decimal(repr(value)) if value is not None else Decimal(0.0)

        potential_field = ''
        if group.is_gwp:
            potential_field = 'substance__gwp'
        elif group.is_odp:
            potential_field = 'substance__odp'

        # This works both faster and more correctly than using Django's
        # aggregations!
        # One SQL query for all fields.
        fields_values = cls.objects.filter(
            submission=submission, substance__group__id=group.id
        ).values(potential_field, *field_names)

        return {
            field_name: float(sum(
                [
                    zero_if_none(value[field_name]) *
                    Decimal(repr(value[potential_field]) if value[potential_field] else 0)
                    for value in fields_values
                ]
            ))
            for field_name in field_names
        }

    @classmethod
    def fill_aggregated_data(cls, submission=None, reported_groups=[]):
        # Aggregations are unique per Party/Period/AnnexGroup. We need to
        # iterate over the substance groups in this submission.

        if not hasattr(cls, 'AGGREGATION_MAPPING'):
            return

        for group in reported_groups:
            # Find an aggregation if one is already created
            aggregation, created = ProdCons.objects.get_or_create(
                party=submission.party,
                reporting_period=submission.reporting_period,
                group=group
            )

            values = cls.get_fields_sum_by_group(
                submission, group, cls.AGGREGATION_MAPPING.keys()
            )
            for model_field, aggr_field in cls.AGGREGATION_MAPPING.items():
                # Add with existing value, as a field in the aggregation
                # table may be populated by aggregating values from several
                # other fields in the data models.
                value = getattr(aggregation, aggr_field) \
                        + values[model_field]
                setattr(aggregation, aggr_field, value)

            form_type = submission.obligation.form_type
            if form_type in aggregation.submissions:
                submissions_set = set(aggregation.submissions[form_type])
                submissions_set.add(submission.id)
                aggregation.submissions[form_type] = list(submissions_set)
            else:
                aggregation.submissions[form_type] = [submission.obligation.id,]

            # This will automatically trigger the calculation of computed
            # values
            aggregation.save()

    @classmethod
    def fill_aggregated_mt_data(cls, submission, queryset):
        if not hasattr(cls, 'AGGREGATION_MAPPING'):
            return

        for entry in queryset:
            # Add entry to dictionary if necessary
            aggregation, created = ProdConsMT.objects.get_or_create(
                party=submission.party,
                reporting_period=submission.reporting_period,
                substance=entry.substance
            )

            for model_field, aggr_field in cls.AGGREGATION_MAPPING.items():
                # Add with existing value, as a field in the aggregation
                # table may be populated by aggregating values from several
                # other fields in the data models.
                model_value = getattr(entry, model_field, None)
                model_value = model_value if model_value else 0.0
                value = getattr(aggregation, aggr_field) + model_value
                setattr(aggregation, aggr_field, value)

            form_type = submission.obligation.form_type
            if form_type in aggregation.submissions:
                submissions_set = set(aggregation.submissions[form_type])
                submissions_set.add(submission.id)
                aggregation.submissions[form_type] = list(submissions_set)
            else:
                aggregation.submissions[form_type] = [submission.obligation.id,]

            # This will automatically trigger the calculation of computed
            # values
            aggregation.save()

    @classmethod
    def clear_aggregated_data(cls, submission, reported_groups=[]):
        """
        Clears all aggregated data generated by submission
        """
        if not hasattr(cls, 'AGGREGATION_MAPPING'):
            return

        for group in reported_groups:
            # Find an aggregation if one is already created
            # This will return None if there is no aggregation
            aggregation = ProdCons.objects.filter(
                party=submission.party,
                reporting_period=submission.reporting_period,
                group=group
            ).first()
            if aggregation is None:
                continue

            # Set all aggregation fields coming from this model to zero
            for model_field, aggr_field in cls.AGGREGATION_MAPPING.items():
                setattr(aggregation, aggr_field, 0.0)

            # Clear this submission from the list of submissions for this aggr
            form_type = submission.obligation.form_type
            if submission.id in aggregation.submissions.get(form_type, []):
                submissions_set = set(aggregation.submissions[form_type])
                submissions_set.remove(submission.id)
                aggregation.submissions[form_type] = list(submissions_set)

            # If this has left the aggregation empty, delete it; else save
            if aggregation.is_empty():
                aggregation.delete()
            else:
                aggregation.save()

    @classmethod
    def clear_aggregated_mt_data(cls, submission, queryset):
        if not hasattr(cls, 'AGGREGATION_MAPPING'):
            return

        for entry in queryset:
            aggregation = ProdConsMT.objects.filter(
                party=submission.party,
                reporting_period=submission.reporting_period,
                substance=entry.substance
            ).first()
            if aggregation is None:
                continue

            # Set all aggregation fields coming from this model to zero
            for model_field, aggr_field in cls.AGGREGATION_MAPPING.items():
                setattr(aggregation, aggr_field, 0.0)

            # Clear this submission from the list of submissions for this aggr
            form_type = submission.obligation.form_type
            if submission.id in aggregation.submissions[form_type]:
                submissions_set = set(aggregation.submissions[form_type])
                submissions_set.remove(submission.id)
                aggregation.submissions[form_type] = list(submissions_set)

            # If this has left the aggregation empty, delete it; else save
            if aggregation.is_empty():
                aggregation.delete()
            else:
                aggregation.save()

    @classmethod
    def get_aggregated_data(cls, submission, reported_groups):
        """
        reported_groups: mapping of form:
        {
            group: ProdCons instance,
            ...
        }
        """
        if not hasattr(cls, 'AGGREGATION_MAPPING'):
            return

        # Aggregations are unique per Party/Period/AnnexGroup. We need to
        # iterate over the substance groups in this submission.
        for group, aggregation in reported_groups.items():
            # Initiate a model instance if needed but *do not save* it to the DB
            # This still initiates the fields with the correct default values.
            if aggregation is None:
                aggregation = ProdCons(
                    party=submission.party,
                    reporting_period=submission.reporting_period,
                    group=group
                )
                reported_groups[group] = aggregation

            values = cls.get_fields_sum_by_group(
                submission, group, cls.AGGREGATION_MAPPING.keys()
            )
            for model_field, aggr_field in cls.AGGREGATION_MAPPING.items():
                # Add with existing value, as a field in the aggregation table
                # may be populated by aggregating values from several other
                # fields in the data models.
                value = getattr(aggregation, aggr_field) + values[model_field]
                setattr(aggregation, aggr_field, value)

            # Populate limits and baselines; calculate totals
            aggregation.populate_limits_and_baselines()
            aggregation.calculate_totals()

    @classmethod
    def get_aggregated_mt_data(cls, submission, queryset, reported_substances):
        """
        reported_substances: mapping of form:
        {
            substance: ProdConsMT instance,
            ...
        }
        """
        if not hasattr(cls, 'AGGREGATION_MAPPING'):
            return

        for entry in queryset:
            # Add entry to dictionary if necessary
            if entry.substance not in reported_substances.keys():
                reported_substances[entry.substance] = ProdConsMT(
                    party=submission.party,
                    reporting_period=submission.reporting_period,
                    substance=entry.substance
                )
            # Now we definitely have an aggregation, update it based on this
            # entry's data
            aggregation = reported_substances[entry.substance]

            for model_field, aggr_field in cls.AGGREGATION_MAPPING.items():
                # Add with existing value, as a field in the aggregation
                # table may be populated by aggregating values from several
                # other fields in the data models.
                model_value = getattr(entry, model_field, None)
                model_value = model_value if model_value else 0.0
                value = getattr(aggregation, aggr_field) + model_value
                setattr(aggregation, aggr_field, value)

            aggregation.calculate_totals()


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
    remarks_party = models.CharField(
        max_length=9999, blank=True,
        help_text="Remarks added by the reporting party"
    )
    remarks_os = models.CharField(
        max_length=9999,
        blank=True,
        help_text="Remarks added by the ozone secretariat"
    )

    ordering_id = models.IntegerField(
        default=0,
        help_text="This allows the interface to keep the data entries in their "
                  "original order, as given by the user."
    )

    class Meta:
        abstract = True
        ordering = ['ordering_id', ]


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
    decision_polyols = models.CharField(
        max_length=512, blank=True
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
    decision_critical_uses = models.CharField(max_length=512, blank=True)

    quantity_essential_uses = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    decision_essential_uses = models.CharField(max_length=512, blank=True)

    quantity_high_ambient_temperature = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    decision_high_ambient_temperature = models.CharField(
        max_length=512, blank=True
    )

    quantity_laboratory_analytical_uses = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    decision_laboratory_analytical_uses = models.CharField(
        max_length=512, blank=True
    )

    quantity_process_agent_uses = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    decision_process_agent_uses = models.CharField(max_length=512, blank=True)

    quantity_quarantine_pre_shipment = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    decision_quarantine_pre_shipment = models.CharField(
        max_length=512, blank=True
    )

    quantity_other_uses = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    decision_other_uses = models.CharField(
        max_length=512, blank=True
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

    has_imports = models.NullBooleanField(
        help_text="If set to true it allows to complete imports data form."
    )

    has_exports = models.NullBooleanField(
        help_text="If set to true it allows to complete exports data form."
    )

    has_produced = models.NullBooleanField(
        help_text="If set to true it allows to complete productions data form."
    )

    has_destroyed = models.NullBooleanField(
        help_text="If set to true it allows to complete destructions data form."
    )

    has_nonparty = models.NullBooleanField(
        help_text="If set to true it allows to complete non-party trades data form."
    )

    has_emissions = models.NullBooleanField(
        help_text="If set to true it allows to complete emissions data form."
    )

    tracker = FieldTracker()

    @property
    def is_filled(self):
        return (
            self.has_imports is not None
            and self.has_exports is not None
            and self.has_produced is not None
            and self.has_destroyed is not None
            and self.has_nonparty is not None
            and self.has_emissions is not None
        )

    class Meta:
        db_table = 'reporting_art7_questionnaire'


class Article7Export(
    AggregationMixin, ModifyPreventionMixin, PolyolsMixin,
    BaseBlendCompositionReport, BaseImportExportReport, BaseUses
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

    # {aggregation_field: data_field_1, ...}
    AGGREGATION_MAPPING = {
        'quantity_total_new': 'export_new',
        'quantity_total_recovered': 'export_recovered',
        'quantity_feedstock': 'export_feedstock',
        'quantity_essential_uses': 'export_essential_uses',
        'quantity_quarantine_pre_shipment': 'export_quarantine',
        'quantity_process_agent_uses': 'export_process_agent'
    }

    # FieldTracker does not work on abstract models
    tracker = FieldTracker()

    destination_party = models.ForeignKey(
        Party,
        null=True,
        blank=True,
        related_name='article7exports_to',
        on_delete=models.PROTECT
    )

    class Meta(BaseReport.Meta):
        db_table = 'reporting_art7_exports'
        ordering = [
            'substance__sort_order', 'substance__substance_id',
            'blend__sort_order'
        ]


class Article7Import(
    AggregationMixin, ModifyPreventionMixin, PolyolsMixin,
    BaseBlendCompositionReport, BaseImportExportReport, BaseUses
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

    # {aggregation_field: data_field_1, ...}
    AGGREGATION_MAPPING = {
        'quantity_total_new': 'import_new',
        'quantity_total_recovered': 'import_recovered',
        'quantity_feedstock': 'import_feedstock',
        'quantity_essential_uses': 'import_essential_uses',
        'quantity_laboratory_analytical_uses': 'import_laboratory_uses',
        'quantity_quarantine_pre_shipment': 'import_quarantine',
        'quantity_process_agent_uses': 'import_process_agent'
    }

    # FieldTracker does not work on abstract models
    tracker = FieldTracker()

    source_party = models.ForeignKey(
        Party,
        null=True,
        blank=True,
        related_name='article7imports_from',
        on_delete=models.PROTECT
    )

    class Meta(BaseReport.Meta):
        db_table = 'reporting_art7_imports'
        ordering = [
            'substance__sort_order', 'substance__substance_id',
            'blend__sort_order'
        ]


class Article7Production(
    AggregationMixin, ModifyPreventionMixin,
    BaseReport, BaseUses
):
    """
    Model for a simple Article 7 data report on production.

    All quantities expressed in metric tonnes.
    """

    AGGREGATION_MAPPING = {
        'quantity_total_produced': 'production_all_new',
        'quantity_feedstock': 'production_feedstock',
        'quantity_essential_uses': 'production_essential_uses',
        'quantity_laboratory_analytical_uses': 'production_laboratory_analytical_uses',
        'quantity_article_5': 'production_article_5',
        'quantity_quarantine_pre_shipment': 'production_quarantine',
        'quantity_process_agent_uses': 'production_process_agent',
    }

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

    class Meta(BaseReport.Meta):
        db_table = 'reporting_art7_production'
        ordering = ['substance__sort_order', 'substance__substance_id']


class Article7Destruction(
    AggregationMixin, ModifyPreventionMixin,
    BaseBlendCompositionReport
):
    """
    Model for a simple Article 7 data report on destruction.

    All quantities expressed in metric tonnes.
    """

    # Needed by the BlendCompositionMixin
    tracker = FieldTracker()

    QUANTITY_FIELDS = [
        'quantity_destroyed',
    ]

    AGGREGATION_MAPPING = {
        'quantity_destroyed': 'destroyed',
    }

    quantity_destroyed = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )

    class Meta(BaseReport.Meta):
        db_table = 'reporting_art7_destruction'
        ordering = ['substance__sort_order', 'substance__substance_id']


class Article7NonPartyTrade(
    AggregationMixin, ModifyPreventionMixin,
    BaseBlendCompositionReport
):
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

    AGGREGATION_MAPPING = {
        'quantity_import_new': 'non_party_import',
        'quantity_import_recovered': 'non_party_import',
        'quantity_export_new': 'non_party_export',
        'quantity_export_recovered': 'non_party_export',
    }

    trade_party = models.ForeignKey(
        Party, blank=True, null=True, on_delete=models.PROTECT
    )

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

    class Meta(BaseReport.Meta):
        db_table = 'reporting_art7_npt'
        ordering = [
            'substance__sort_order', 'substance__substance_id',
            'blend__sort_order'
        ]

    def clean(self):
        if self.submission.schema_version != 'legacy' and not (
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
        # Don't do any checks for uncontrolled substances (group is None)
        if (
            not self.blend and self.substance and self.trade_party
            and self.submission.schema_version != 'legacy'
            and self.substance.group
        ):
            non_parties = self.substance.group.get_non_parties()
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

    class Meta(BaseReport.Meta):
        db_table = 'reporting_art7_emissions'


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

    class Meta(BaseReport.Meta):
        db_table = 'reporting_hat_production'
        ordering = ['substance__sort_order', 'substance__substance_id']


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

    class Meta(BaseReport.Meta):
        db_table = 'reporting_hat_import'
        ordering = [
            'substance__sort_order', 'substance__substance_id',
            'blend__sort_order'
        ]


class DataOther(ModifyPreventionMixin, BaseReport):
    """
    Model for Data Other reports.
    """

    tracker = FieldTracker()

    class Meta:
        db_table = 'reporting_other'


class RAFReport(ModifyPreventionMixin, BaseReport):
    """
    Model for RAF reports.

    These behave the same as Article 7 reports in regards to workflow, cloning,
    etc.
    """

    # These reports only refer to substances
    substance = models.ForeignKey(Substance, on_delete=models.PROTECT)

    # criticality is inferred from substance, only emergency flag is needed
    is_emergency = models.BooleanField(default=False)

    quantity_exempted = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )

    quantity_production = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )

    quantity_used = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )

    quantity_exported = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )

    quantity_destroyed = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )

    on_hand_start_year = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )

    tracker = FieldTracker()

    @property
    def quantity_imports(self):
        if self.imports:
            return sum([imp.get('quantity', 0) for imp in self.imports])
        return 0

    @property
    def is_critical(self):
        return self.substance.has_critical_uses

    class Meta:
        db_table = 'reporting_raf'
        ordering = ['substance__sort_order', 'substance__substance_id']


class RAFReportUseCategory(ModifyPreventionMixin, models.Model):
    """
    Breakdown of `quantity_used` from a RAFReport, based on critical use
    category.

    Only allowed for critical use RAF reports.
    """
    report = models.ForeignKey(
        RAFReport,
        related_name='use_categories',
        on_delete=models.CASCADE
    )

    critical_use_category = models.ForeignKey(
        CriticalUseCategory,
        related_name='use_categories',
        on_delete=models.CASCADE
    )

    quantity = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )

    tracker = FieldTracker()

    @property
    def submission(self):
        """
        This is necessary for ModifyPreventionMixin to work properly.
        """
        return self.report.submission

    def clean(self):
        """
        Ensure that use category breakdowns are only saved for critical uses.
        """
        if not self.report.is_critical:
            raise ValidationError(
                _(
                    "Breakdown per critical use category can only be saved for "
                    "critical reports!"
                )
            )
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'reporting_raf_use_category'


class RAFImport(ModifyPreventionMixin, models.Model):
    """
    This is used for modelling multiple import quantities/country of origin
    pairs on each RAFReport row.

    Substance is the one from the RAFReport entry, so no need for it here.
    """
    report = models.ForeignKey(
        RAFReport, blank=False, null=False, on_delete=models.CASCADE,
        related_name='imports'
    )

    party = models.ForeignKey(
        Party,
        blank=True,
        null=True,
        on_delete=models.PROTECT
    )

    # This needs to have a quantity specified
    quantity = models.FloatField(validators=[MinValueValidator(0.0)])

    tracker = FieldTracker()

    @property
    def submission(self):
        """
        This is necessary for ModifyPreventionMixin to work properly.
        """
        return self.report.submission

    class Meta:
        db_table = 'reporting_raf_import'
