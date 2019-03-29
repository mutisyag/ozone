import datetime

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .legal import ReportingPeriod
from .meeting import Treaty
from .utils import RatificationTypes


__all__ = [
    'Region',
    'Subregion',
    'Party',
    'PartyHistory',
    'Language',
    'PartyRatification',
    'PartyType',
    'Language',
]


class PartyType(models.Model):
    """
    Party classification.

    Using a model instead of an enum allows for more flexibility.

    A5 = 'Article 5'
    A5G1 = 'Article 5 Group 1'
    A5G2 = 'Article 5 Group 2'
    NA5 = 'Non Article 5'
    NA5G1 = 'Non Article 5 Group 1'
    NA5G2 = 'Non Article 5 Group 2'
    """

    abbr = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'party_type'


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
        db_table = 'region'


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
        db_table = 'subregion'


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

    # Some parties (e.g. EU) can encompass several other full-featured parties
    # TODO: come up with better name (and better related_name)
    parent_party = models.ForeignKey(
        'self',
        related_name='child_parties',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    remark = models.CharField(max_length=9999, blank=True)

    @classmethod
    def get_main_parties(cls):
        return cls.objects.filter(id=models.F('parent_party_id'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'parties'
        ordering = ('name',)
        db_table = 'party'


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

    # This will still require form choices to be generated based on the same
    # start year.
    reporting_period = models.ForeignKey(
        ReportingPeriod,
        related_name='party_histories',
        on_delete=models.PROTECT
    )

    party_type = models.ForeignKey(
        PartyType,
        related_name='party_histories',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    population = models.FloatField(validators=[MinValueValidator(0.0)])

    is_high_ambient_temperature = models.BooleanField()

    # Reflects EU membership for that specific year
    is_eu_member = models.BooleanField()

    # Reflects Country Economy In Transition for that specific year
    is_ceit = models.BooleanField()

    is_article5 = models.BooleanField()

    # Remarks
    remark = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return f'{self.party.name} - {self.reporting_period}'

    class Meta:
        unique_together = ('party', 'reporting_period')
        ordering = ('party', 'reporting_period')
        verbose_name_plural = 'parties history'
        db_table = 'party_history'


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

    ratification_date = models.DateField()

    entry_into_force_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'party_ratification'


class Language(models.Model):
    """
    Model for languages used by Ozone Secretariat.
    """

    # This is a sane default (English language) based on the current fixtures
    DEFAULT_LANGUAGE_ID = 3

    language_id = models.CharField(max_length=16, unique=True)

    iso = models.CharField(max_length=5, unique=True)

    name = models.CharField(max_length=64, unique=True)

    remark = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        db_table = 'language'
