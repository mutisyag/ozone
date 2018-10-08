import datetime
import enum

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .meeting import Treaty
from .substance import Substance, Group, Annex
from .utils import RatificationTypes


__all__ = [
    'Region',
    'Subregion',
    'Party',
    'UsesType',
    'PartyHistory',
    'Language',
    'Nomination',
    'PartyRatification',
    'PartyTypes',
]


@enum.unique
class PartyTypes(enum.Enum):
    """
    Party classification.
    """

    A5 = 'Article 5'
    A5G1 = 'Article 5 Group 1'
    A5G2 = 'Article 5 Group 2'
    NA5 = 'Non Article 5'


class Region(models.Model):
    """
    Regions for reporting countries.

    Seems a bit overkill to create a model for these, but it offers more
    flexibility and easier maintenance.
    """

    abbr = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=256, unique=True)

    remark = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Subregion(models.Model):
    """
    Sub-regions for reporting countries.

    Seems a bit overkill to create a model for these, but it offers more
    flexibility and easier maintenance.
    """

    abbr = models.CharField(max_length=32)
    name = models.CharField(max_length=256)

    region = models.ForeignKey(
        Region, related_name='subregions', on_delete=models.PROTECT
    )

    remark = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return f'{self.region.name} - subregion {self.name}'

    class Meta:
        unique_together = ('abbr', 'region')
        ordering = ('region', 'name')


class Party(models.Model):
    """
    Reporting Party (generally country)
    """
    name = models.CharField(max_length=256, unique=True)
    abbr = models.CharField(max_length=32, unique=True)

    # Subregion also includes region information
    subregion = models.ForeignKey(
        Subregion, related_name='parties', on_delete=models.PROTECT
    )

    # TODO:
    # What are:
    # - CntryID_org ?
    # - CntryName20 - name truncated to 20 - no need for it
    # - MDG_CntryCode(Int) (both are the same)
    # - ISO alpha3 code?
    # - www_country_id ???

    # Some parties (e.g. EU) can encompass several other full-featured parties
    # TODO: come up with better name (and better related_name)
    parent_party = models.ForeignKey(
        'self',
        related_name='child_parties',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    # Ratification information
    signed_vienna_convention = models.DateField(blank=True, null=True)
    ratification_date_vienna_convention = models.DateField(
        blank=True, null=True
    )
    ratification_type_vienna_convention = models.CharField(
        max_length=40,
        choices=((s.value, s.name) for s in RatificationTypes),
        blank=True
    )

    signed_montreal_protocol = models.DateField(blank=True, null=True)
    ratification_date_montreal_protocol = models.DateField(
        blank=True, null=True
    )
    ratification_type_montreal_protocol = models.CharField(
        max_length=40,
        choices=((s.value, s.name) for s in RatificationTypes),
        blank=True
    )

    ratification_date_london_amendment = models.DateField(
        blank=True, null=True
    )
    ratification_type_london_amendment = models.CharField(
        max_length=40,
        choices=((s.value, s.name) for s in RatificationTypes),
        blank=True
    )

    ratification_date_copenhagen_amendment = models.DateField(
        blank=True, null=True
    )
    ratification_type_copenhagen_amendment = models.CharField(
        max_length=40,
        choices=((s.value, s.name) for s in RatificationTypes),
        blank=True
    )

    ratification_date_montreal_amendment = models.DateField(
        blank=True, null=True
    )
    ratification_type_montreal_amendment = models.CharField(
        max_length=40,
        choices=((s.value, s.name) for s in RatificationTypes),
        blank=True
    )

    ratification_date_beijing_amendment = models.DateField(
        blank=True, null=True
    )
    ratification_type_beijing_amendment = models.CharField(
        max_length=40,
        choices=((s.value, s.name) for s in RatificationTypes),
        blank=True
    )

    ratification_date_kigali_amendment = models.DateField(
        blank=True, null=True
    )
    ratification_type_kigali_amendment = models.CharField(
        max_length=40,
        choices=((s.value, s.name) for s in RatificationTypes),
        blank=True
    )

    remark = models.CharField(max_length=512, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'parties'
        ordering = ('name',)


def current_year():
    return datetime.date.today().year


def max_value_current_year(value):
    """
    Wrapping the MaxValueValidator in a function avoids a new migration
    every year.
    """
    return MaxValueValidator(current_year())(value)


class PartyHistory(models.Model):
    """
    Detailed Party information, per year (population, flags etc) can change
    based on the specified period.
    """

    party = models.ForeignKey(
        Party, related_name='history', on_delete=models.PROTECT
    )

    # TODO: should use a ForeignKey to `ReportingPeriod` instead? don't think so
    # This will still require form choices to be generated based on the same
    # start year.
    year = models.IntegerField(
        validators=[MinValueValidator, max_value_current_year]
    )

    population = models.FloatField(validators=[MinValueValidator(0.0)])

    party_type = models.CharField(
        max_length=40,
        choices=((s.value, s.name) for s in PartyTypes),
        blank=True
    )

    is_high_ambient_temperature = models.BooleanField()

    # Reflects EU membership for that specific year
    is_eu_member = models.BooleanField()

    # Reflects Country Economy In Transition for that specific year
    is_ceit = models.BooleanField()

    # Remarks
    remark = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return f'{self.party.name} - {self.year}'

    class Meta:
        unique_together = ('party', 'year')
        ordering = ('party', 'year')
        verbose_name_plural = 'parties history'


class PartyRatification(models.Model):
    """
    Ratification information of all treaties and amendments, for each party.
    """

    party = models.ForeignKey(
        Party, related_name='ratifications', on_delete=models.PROTECT
    )

    treaty = models.ForeignKey(
        Treaty, related_name='ratifications', on_delete=models.PROTECT
    )

    ratification_type = models.CharField(
        max_length=40,
        choices=((s.value, s.name) for s in RatificationTypes),
        blank=True
    )

    date = models.DateField()


class Language(models.Model):
    """
    Model for languages used by Ozone Secretariat.
    """

    language_id = models.CharField(max_length=16, unique=True)

    name = models.CharField(max_length=64, unique=True)

    remark = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class UsesType(models.Model):
    """
    The different categories of uses of controlled substances that need to be reported.
    """

    uses_type_id = models.CharField(max_length=16, unique=True)

    name = models.CharField(max_length=128, unique=True)

    remark = models.CharField(max_length=256, blank=True)

    decision_flag = models.BooleanField()

    forms = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Nomination(models.Model):
    """
    Submitted by a Party for an Exemption.
    """

    nomination_id = models.CharField(max_length=16, unique=True)

    party = models.ForeignKey(
        Party, related_name='nominations', on_delete=models.PROTECT
    )

    reporting_period = models.ForeignKey(
        'core.ReportingPeriod', related_name='nominations', on_delete=models.PROTECT
    )

    uses_type = models.ForeignKey(
        UsesType, related_name='nominations', on_delete=models.PROTECT
    )

    substance = models.ForeignKey(
        Substance, null=True, on_delete=models.PROTECT
    )

    submit_date = models.DateField()

    submit_amt = models.FloatField()

    remark = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return self.nomination_id

    class Meta:
        ordering = ('nomination_id',)


class ControlMeasure(models.Model):
    """
    Restrictions on level of production and consumption for Parties.
    """

    party = models.ForeignKey(
        Party, on_delete=models.PROTECT
    )

    group = models.ForeignKey(
        Group, on_delete=models.PROTECT
    )

    reporting_period = models.ForeignKey(
        'core.ReportingPeriod', on_delete=models.PROTECT
    )

    production_allowed = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    consumption_allowed = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    basic_domestic_needs_allowed = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        blank=True, null=True
    )


class BaseExemption(models.Model):

    party = models.ForeignKey(
        Party, related_name='%(class)ss', on_delete=models.PROTECT
    )

    reporting_period = models.ForeignKey(
        'core.ReportingPeriod', on_delete=models.PROTECT
    )

    substance = models.ForeignKey(
        Substance, on_delete=models.PROTECT
    )

    uses_type = models.ForeignKey(
        UsesType, on_delete=models.PROTECT
    )

    critical_uses_category = models.CharField(max_length=256, blank=True)

    remark = models.CharField(max_length=256, blank=True)

    class Meta:
        abstract = True


class ExemptionApproved(BaseExemption):

    emergency = models.BooleanField(default=False)

    approved_teap_amount = models.FloatField(
        validators=[MinValueValidator(0.0)]
    )
    approved_amount = models.FloatField(
        validators=[MinValueValidator(0.0)]
    )
    decision_approved = models.CharField(max_length=256, blank=True)

    laboratory_analytical_uses_category = models.CharField(max_length=256, blank=True)


class ExemptionReported(BaseExemption):

    import_party = models.ForeignKey(
        Party, on_delete=models.PROTECT
    )

    quantity_exempted = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    quantity_produced = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    quantity_imported = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    # TODO: what is this?
    quantity_open_bal = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    quantity_essential_uses = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    quantity_exported = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    quantity_destroyed = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )


class Limit(models.Model):
    """
    Production and Consumption Limits for Substances in a Group / Annex,
    for a Period, for a Party (EDT)
    """

    party = models.ForeignKey(
        Party, on_delete=models.PROTECT
    )
    reporting_period = models.ForeignKey(
        'core.ReportingPeriod', on_delete=models.PROTECT
    )
    group = models.ForeignKey(
        Group, on_delete=models.PROTECT
    )

    production = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True

    )
    consumption = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    basic_domestic_needs_production = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )


class ProcessAgentEmitLimit(models.Model):
    """
    Emission limits for process agent uses, for non-Article 5 parties.
    """

    party = models.ForeignKey(
        Party, on_delete=models.PROTECT
    )

    decision = models.CharField(max_length=256)

    makeup_consumption = models.FloatField(validators=[MinValueValidator(0.0)])

    max_emissions = models.FloatField(validators=[MinValueValidator(0.0)])

    remark = models.CharField(max_length=512, blank=True)


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

    substance = models.ForeignKey(
        Substance, on_delete=models.PROTECT
    )

    reporting_period = models.ForeignKey(
        'core.ReportingPeriod', related_name='transfers', on_delete=models.PROTECT
    )

    transferred_amount = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )
    used_amount = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=True, null=True
    )

    is_basic_domestic_need = models.BooleanField(default=False)

    source_party = models.ForeignKey(
        Party, related_name='sent_transfers', on_delete=models.PROTECT
    )
    destination_party = models.ForeignKey(
        Party, related_name='received_transfers', on_delete=models.PROTECT
    )

    remark = models.CharField(max_length=512, blank=True)
