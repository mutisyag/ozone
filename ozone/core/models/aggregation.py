from datetime import datetime
from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator

from .legal import ReportingPeriod
from .party import Party, PartyHistory
from .substance import Group
from .utils import round_half_up
from .control import Limit, LimitTypes, Baseline, BaselineType


__all__ = [
    'ProdCons',
]


class ProdCons(models.Model):
    """
    Aggregation for Production/consumption data reports.

    Only one entry per party/reporting_period/group - when a new submission
    becomes current for that party & reporting period, the values in the entry
    will be automatically updated.
    """

    party = models.ForeignKey(
        Party,
        related_name="prod_cons_aggregations",
        on_delete=models.PROTECT,
        help_text="Party for which this aggregation was calculated",
    )

    reporting_period = models.ForeignKey(
        ReportingPeriod,
        related_name="prod_cons_aggregations",
        on_delete=models.PROTECT,
        help_text="Reporting Period for which this aggregation was calculated",
    )

    group = models.ForeignKey(
        Group,
        related_name="prod_cons_aggregations",
        on_delete=models.PROTECT,
        help_text="Annex Group for which this aggregation was calculated",
    )

    # Aggregated quantity fields (derived from data reports)
    # Production
    production_all_new = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0)]
    )

    production_feedstock = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0)]
    )

    production_essential_uses = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0)]
    )

    production_laboratory_analytical_uses = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0)]
    )

    production_article_5 = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0)]
    )

    production_quarantine = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0)]
    )

    production_process_agent = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0)]
    )

    # Destruction
    destroyed = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0)]
    )

    # Imports
    import_new = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0)]
    )

    import_recovered = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0)]
    )

    import_feedstock = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0)]
    )

    import_essential_uses = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0)]
    )

    import_laboratory_uses = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0)]
    )

    import_quarantine = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0)]
    )

    import_process_agent = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0)]
    )

    # Exports
    export_new = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0)]
    )

    export_recovered = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0)]
    )

    export_feedstock = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0)]
    )

    export_essential_uses = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0)]
    )

    export_quarantine = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0)]
    )

    export_process_agent = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0)]
    )

    # Non-party: these values are an aggregation of art7 non-party trade
    # ([import/export]_[new/recovered])
    non_party_import = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0)]
    )

    non_party_export = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0)]
    )

    # Prod transfer
    prod_transfer = models.FloatField(
        default=0.0, validators=[MinValueValidator(0.0)]
    )

    # Baselines - they can be null!
    baseline_prod = models.FloatField(blank=True, null=True, default=None)

    baseline_cons = models.FloatField(blank=True, null=True, default=None)

    baseline_bdn = models.FloatField(blank=True, null=True, default=None)

    # Limits
    limit_prod = models.FloatField(blank=True, null=True, default=None)

    limit_cons = models.FloatField(blank=True, null=True, default=None)

    limit_bdn = models.FloatField(blank=True, null=True, default=None)

    # Totals computed based on the above fields.
    # Though these could have been implemented as properties (as they can be
    # deterministically derived from the values of the above fields), having
    # them as fields in the models allows greater flexibility in use.
    # They are null-able so entries can be saved without these being calculated.
    calculated_production = models.FloatField(
        null=True, blank=True, default=None
    )

    calculated_consumption = models.FloatField(
        null=True, blank=True, default=None
    )

    @classmethod
    def cleanup_aggregations(cls, party, reporting_period):
        """
        This resets all aggregation data for the given party/period.

        For now this simply means deleting all corresponding rows, but this might
        change in the future if more data sources (besides Art7) are added
        """
        cls.objects.filter(
            party=party, reporting_period=reporting_period
        ).delete()

    @classmethod
    def get_decimals(cls, period, group, party):
        """
        Returns the number of decimals according to the following rounding rules.
        """

        special_cases_2009 = [
            'CD', 'CG', 'DZ', 'EC', 'ER', 'GQ', 'GW', 'HT', 'LC', 'MA', 'MK',
            'MZ', 'NE', 'NG', 'SZ', 'FJ', 'PK', 'PH'
        ]
        special_cases_2010 = [
            'DZ', 'EC', 'ER', 'HT', 'LC', 'LY', 'MA', 'NG', 'PE', 'SZ', 'TR',
            'YE', 'FJ', 'PK', 'PH'
        ]
        if group.group_id == 'CI':
            if (
                period.start_date >= datetime.strptime('2011-01-01', "%Y-%m-%d").date()
                or period.name == '2009' and party.abbr in special_cases_2009
                or period.name == '2010' and party.abbr in special_cases_2010
            ):
                return 2
        return 1

    @staticmethod
    def has_read_rights_for_party(party, user):
        if (
            user.is_secretariat
            or user.party is not None and user.party == party
        ):
            return True
        return False

    def has_read_rights(self, user):
        return self.has_read_rights_for_party(self.party, user)

    @property
    def is_european_union(self):
        return self.party == Party.objects.get(abbr="ECE")

    @property
    def is_after_2010(self):
        rp_2010 = ReportingPeriod.objects.get(name="2010")
        if self.reporting_period.start_date >= rp_2010.start_date:
            return True
        return False

    @property
    def is_china_or_brazil(self):
        return (
            self.party == Party.objects.get(abbr="CN")
            or self.party == Party.objects.get(abbr="BR")
        )

    def get_production_process_agent(self, is_article_5):
        if not is_article_5 or (self.is_china_or_brazil and self.is_after_2010):
            return self.production_process_agent
        return 0.0

    def get_import_process_agent(self, is_article_5):
        if not is_article_5 or (self.is_china_or_brazil and self.is_after_2010):
            return self.import_process_agent
        return 0.0

    def get_export_feedstock(self):
        return self.export_feedstock if self.production_all_new > 0.0 else 0.0

    def get_export_process_agent(self):
        return self.export_process_agent if self.production_all_new > 0.0 \
            else 0.0

    def get_export_quarantine(self):
        return self.export_quarantine if self.production_quarantine > 0.0 \
            else 0.0

    def calculate_totals(self):
        """
        Called on save() to automatically update fields.
        Calculates values for:
            - calculated_production
            - calculated_consumption
        """
        # Get the party's characteristics for this specific reporting period
        party = PartyHistory.objects.get(
            party=self.party, reporting_period=self.reporting_period
        )

        # Production
        if self.is_european_union:
            self.calculated_production = None
        else:
            self.calculated_production = float(
                Decimal(repr(self.production_all_new))
                - Decimal(repr(self.production_feedstock))
                - Decimal(repr(self.production_quarantine))
                - Decimal(repr(self.get_production_process_agent(party.is_article5)))
                - Decimal(repr(self.destroyed))
                - Decimal(repr(self.get_export_feedstock()))
                - Decimal(repr(self.get_export_process_agent()))
            )

        # Consumption
        if party.is_eu_member:
            self.calculated_consumption = None
        else:
            self.calculated_consumption = float(
                Decimal(repr(self.production_all_new))
                - Decimal(repr(self.production_feedstock))
                - Decimal(repr(self.production_quarantine))
                - Decimal(repr(self.get_production_process_agent(party.is_article5)))
                - Decimal(repr(self.destroyed))
                - Decimal(repr(self.export_new))
                + Decimal(repr(self.get_export_quarantine()))
                + Decimal(repr(self.non_party_export))
                + Decimal(repr(self.import_new))
                - Decimal(repr(self.import_feedstock))
                - Decimal(repr(self.get_import_process_agent(party.is_article5)))
                - Decimal(repr(self.import_quarantine))
            )
        self.apply_rounding()

    def apply_rounding(self):
        for field_name in self.get_roundable_fields():
            field_value = getattr(self, field_name)
            if field_value is not None and field_value != '':
                decimals = ProdCons.get_decimals(
                    self.reporting_period, self.group, self.party
                )
                setattr(self, field_name, round_half_up(field_value, decimals))

    def get_roundable_fields(self):
        """
        Returns list of field names which need to be rounded.
        """
        return [
            'baseline_prod',
            'baseline_cons',
            'baseline_bdn',
            'limit_prod',
            'limit_cons',
            'limit_bdn',
            'calculated_production',
            'calculated_consumption',
        ]

    def populate_limits_and_baselines(self):
        """
        At first save we fetch the limits/baselines from the corresponding
        tables.

        This assumes that said tables are pre-populated, which should happen
        in practice. Otherwise, this method might be triggered by other means.
        """
        # Get the party's characteristics for this specific reporting period
        party = PartyHistory.objects.get(
            party=self.party, reporting_period=self.reporting_period
        )

        # Populate limits
        for limit in Limit.objects.filter(
            party=self.party,
            reporting_period=self.reporting_period,
            group=self.group
        ):
            if limit.limit_type == LimitTypes.PRODUCTION.value:
                self.limit_prod = limit.limit
            elif limit.limit_type == LimitTypes.CONSUMPTION.value:
                self.limit_cons = limit.limit
            elif limit.limit_type == LimitTypes.BDN.value:
                self.limit_bdn = limit.limit

        # Populate baselines; first get appropriate baseline types
        if party.is_article5:
            prod_bt = BaselineType.objects.get(name='A5Prod')
            cons_bt = BaselineType.objects.get(name='A5Cons')
            # Non-existent name
            bdn_bt = None
        else:
            prod_bt = BaselineType.objects.get(name='NA5Prod')
            cons_bt = BaselineType.objects.get(name='NA5Cons')
            bdn_bt = BaselineType.objects.get(name='BDN_NA5')

        baselines = Baseline.objects.filter(
            party=self.party,
            group=self.group
        )
        prod = baselines.filter(baseline_type=prod_bt).first()
        cons = baselines.filter(baseline_type=cons_bt).first()
        bdn = baselines.filter(baseline_type=bdn_bt).first()

        if prod:
            self.baseline_prod = prod.baseline
        if cons:
            self.baseline_cons = cons.baseline
        if bdn:
            self.baseline_bdn = bdn.baseline

    def save(
        self,
        force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """
        At each save, we need to recalculate the totals.
        """
        self.calculate_totals()

        # If this is first save, also populate baselines and limits.
        if not self.pk or force_insert:
            self.populate_limits_and_baselines()

        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        db_table = "aggregation_prod_cons"
        unique_together = ("party", "reporting_period", "group")
