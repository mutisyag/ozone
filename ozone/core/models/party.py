import datetime
import enum

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .meeting import Treaty
from .utils import RatificationTypes


__all__ = [
    'Region',
    'Subregion',
    'Party',
    'PartyHistory',
    'Language',
    'PartyRatification',
    'PartyTypes',
    'Language',
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
