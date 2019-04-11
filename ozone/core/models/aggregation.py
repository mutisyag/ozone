from django.db import models
from django.core.validators import MinValueValidator

from .legal import ReportingPeriod
from .party import Party, PartyHistory
from .substance import Group


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

    def get_production_quarantine(self):
        return self.production_quarantine if self.export_quarantine > 0.0 \
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
            self.calculated_production = (
                self.production_all_new
                - self.production_feedstock
                - self.production_quarantine
                - self.get_production_process_agent(party.is_article5)
                - self.destroyed
                - self.get_export_feedstock()
                - self.get_export_process_agent()
            )

        # Consumption
        if party.is_eu_member:
            self.calculated_consumption = None
        else:
            self.calculated_consumption = (
                self.production_all_new
                - self.production_feedstock
                - self.production_quarantine
                - self.get_production_process_agent(party.is_article5)
                - self.destroyed
                - self.export_new
                - self.get_production_quarantine()
                + self.non_party_export
                + self.import_new
                - self.import_feedstock
                - self.get_import_process_agent(party.is_article5)
                - self.import_quarantine
            )

    def save(self, *args, **kwargs):
        """
        At each save, we need to recalculate the totals.
        """
        self.calculate_totals()

        super().save(*args, **kwargs)

    class Meta:
        db_table = "aggregation_prod_cons"
        unique_together = ("party", "reporting_period", "group")