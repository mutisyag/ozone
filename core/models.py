import datetime
import enum

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

#TODO: the cookiecutter did something, but maybe improvement is needed. CHECK!
from ..ozone.users.models import User

# Party time!

class Region(models.Model):
    """
    Regions for reporting countries.

    Seems a bit overkill to create a model for these, but it offers more
    flexibility and easier maintenance.
    """

    name = models.CharField(max_length=256, unique=True)
    # It needs `null=True` to ensure uniqueness constraint is not violated
    # by blank fields. `blank=True` ensures forms accept empty strings.
    abbr = models.CharField(max_length=32, unique=True, blank=True, null=True)


class Subregion(models.Model):
    """
    Sub-regions for reporting countries.

    Seems a bit overkill to create a model for these, but it offers more
    flexibility and easier maintenance.
    """

    name = models.CharField(max_length=256, unique=True)
    # Since it can be blank but is unique, it also has to be nullable
    abbr = models.CharField(max_length=32, unique=True, blank=True, null=True)

    region = models.ForeignKey(
        Region, related_name='subregions', on_delete=models.PROTECT
    )

    def __str__(self):
        return f'Subregion "{self.name}", region "{self.region.name}"'


@enum.unique
class RatificationTypes(enum.Enum):
    """
    General enum of ratification types; should be useful in other models too
    """

    ACCESSION = 'Accession'
    APPROVAL = 'Approval'
    ACCEPTANCE = 'Acceptance'
    RATIFICATION = 'Ratification'
    SUCCESSION = 'Succession'
    SIGNING = 'Signing'


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

    #TODO:
    # What are:
    # - CntryID_org ?
    # - CntryName20 - name truncated to 20 - no need for it
    # - MDG_CntryCode(Int) (both are the same)
    # - ISO alpha3 code?
    # - www_country_id ???

    # Some parties (e.g. EU) can encompass several other full-featured parties
    #TODO: come up with better name (and better related_name)
    parent_party = models.ForeignKey(
        'self', related_name='child_parties', null=True,
        on_delete=models.SET_NULL
    )

    # Ratification information
    signed_vienna_convention = models.DateField(null=True)
    ratification_date_vienna_convention = models.DateField(null=True)
    ratification_type_vienna_convention = models.CharField(
        max_length=40, choices=((s.value, s.name) for s in RatificationTypes)
    )

    signed_montreal_protocol = models.DateField(null=True)
    ratification_date_montreal_protocol = models.DateField(null=True)
    ratification_type_montreal_protocol =  models.CharField(
        max_length=40, choices=((s.value, s.name) for s in RatificationTypes)
    )

    ratification_date_london_amendment = models.DateField(null=True)
    ratification_type_london_amendment = models.CharField(
        max_length=40, choices=((s.value, s.name) for s in RatificationTypes)
    )

    ratification_date_copenhagen_amendment = models.DateField(null=True)
    ratification_type_copenhagen_amendment = models.CharField(
        max_length=40, choices=((s.value, s.name) for s in RatificationTypes)
    )

    ratification_date_montreal_amendment = models.DateField(null=True)
    ratification_type_montreal_amendment = models.CharField(
        max_length=40, choices=((s.value, s.name) for s in RatificationTypes)
    )

    ratification_date_beijing_amendment = models.DateField(null=True)
    ratification_type_beijing_amendment = models.CharField(
        max_length=40, choices=((s.value, s.name) for s in RatificationTypes)
    )

    remarks = models.CharField(max_length=512, blank=True)


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

    population = models.PositiveIntegerField()

    # Reflects Article 5 status for that specific year
    is_article_5 = models.BooleanField()

    # Reflects EU membership for that specific year
    is_eu_member = models.BooleanField()

    # Reflects Country Economy In Transition for that specific year
    is_ceit = models.BooleanField()

    # Remarks
    remark = models.CharField(max_length=256, blank=True)


# Base reporting models: period, obligation etc

class ReportingPeriod(models.Model):
    """
    Period for which data is submitted.

    There is definitely a need to support non-standard reporting periods.
    """

    # This will usually be '2017', '2018' etc; most periods (but not all!)
    # are mapped to calendar years
    name = models.CharField(max_length=64, unique=True)
    # indicates a "normal" (yearly) reporting period, to avoid need of extra
    # logic on the `name` field
    is_year = models.BooleanField(default=True)

    # this is always required, and can be in the future
    start_date = models.DateField()

    # we are always working with 'closed' reporting periods
    # TODO: is above assumption really true? what about one-time reports?
    # I guess those could have no reporting period
    end_date = models.DateField()

    description = models.CharField(max_length=256, blank=True)


class Obligation(models.Model):
    '''
    TODO: add desc
    `data_forms` will point to all data forms filled in for
    this obligation.
    '''
    name = models.CharField(max_length=256, unique=True)
    # TODO: obligation-party mapping!


class Submission(models.Model):
    """
    One specific data submission (version!)
    """

    @enum.unique
    class SubmissionMethods(enum.Enum):
        """
        Enumeration of submission types
        """
        WEBFORM = 'Web form'
        EMAIL = 'Email'

    # TODO: this implements the `submission_type` field from the
    # Ozone Business Data Tables. Analyze how Party-to-Obligation/Version
    # mappings should be modeled.
    obligation = models.ForeignKey(
        Obligation, related_name='submissions', on_delete=models.PROTECT
    )

    # TODO (related to the above):
    # It looks like the simplest (best?) solution for handling
    # reporting format changes (i.e. schema versions) is to keep separate
    # models&tables for each such version.
    # Should investigate whether what's described above is a sane solution.
    schema_version = models.CharField(max_length=64)

    reporting_period = models.ForeignKey(
        ReportingPeriod, related_name='submissions', on_delete=models.PROTECT
    )

    # `party` is always the Party for which data is reported
    party = models.ForeignKey(
        Party, related_name='submissions', on_delete=models.PROTECT
    )
    # data might be received through physical mail; also, OS might decide to
    # make minor modifications on Party's submissions.
    filled_by_secretariat = models.BooleanField(default=False)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    last_edited_by = models.ForeignKey(User, on_delete=models.PROTECT)

    # per Obligation-ReportingPeriod-Party
    #TODO: auto-increment version on save()
    version = models.PositiveSmallIntegerField(default=1)

    #TODO: make this workflow-based, including logic on save()
    status = models.CharField(max_length=64)

    flag_provisional = models.BooleanField(default=False)
    flag_valid = models.BooleanField(default=False)
    flag_superseded = models.BooleanField(default=False)

    submitted_via = models.CharField(
        max_length=32,
        choices=((s.value, s.name) for s in SubmissionMethods)
    )

    # We want these to be able to be empty in forms
    remarks_party = models.CharField(max_length=256, blank=True)
    remarks_secretariat = models.CharField(max_length=256, blank=True)


# MEETINGS & FRIENDS

class Meeting (models.Model):
    """
    Information on Ozone-related meetings
    """

    meeting_id = models.CharField(max_length=16, unique=True)

    treaty_flag = models.BooleanField(default=False)

    # Two existing data fields have null start/end dates
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    # No need for anything else than a CharField
    location = models.CharField(max_length=128)

    description = models.CharField(max_length=128)


class Treaty(models.Model):
    """
    Information on Ozone-related treaties
    """

    treaty_id = models.CharField(max_length=16, unique=True)

    name = models.CharField(max_length=64, unique=True)

    meeting_id = models.ForeignKey(
        Meeting, related_name='treaty', on_delete=models.PROTECT
    )

    date = models.DateField()

    entry_into_force_date = models.DateField()

    base_year = models.IntegerField(null=True)

    description = models.CharField(max_length=256, blank=True)


# SUBSTANCES! YAY!

class Annex(models.Model):
    """
    Substance Annex information
    """
    annex_id = models.CharField(max_length=16, unique=True)

    name = models.CharField(max_length=64, unique=True)

    description = models.CharField(max_length=256, blank=True)


class Group(models.Model):
    """
    Substance Group information
    """
    group_id = models.CharField(max_length=16, unique=True)

    annex = models.ForeignKey(
        Annex, related_name='groups', on_delete=models.PROTECT
    )

    description = models.CharField(max_length=256)

    control_treaty = models.ForeignKey(
        Treaty, related_name='control_substance_groups', on_delete=models.PROTECT
    )
    report_treaty = models.ForeignKey(
        Treaty, related_name='report_substance_groups', on_delete=models.PROTECT
    )

    phase_out_year_article_5 = models.DateField(null=True)
    phase_out_year_non_article_5 = models.DateField(null=True)

    # TODO: should this be a foreign key?
    exemption = models.CharField(max_length=64, blank=True)

    # TODO: figure out a way to model consumption and production baselines.
    # These will probably have to sit in a special table, with foreign keys
    # to parties and Group IDs


class Substance(models.Model):
    """
    Stores all info for a specific substance
    """

    substance_id = models.IntegerField(unique=True)

    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=256)

    # In the existing data tables there is a special case:
    # the 'Other Substances' dummy substance, for which these can be null.
    # That should be modeled differently, by a nullable foreign key to
    # `Substance`, instead of making a lot of fields nullable in this model.
    annex_id = models.ForeignKey(
        Annex, related_name='substances', on_delete=models.PROTECT
    )
    group_id = models.ForeignKey(
        Group, related_name='substances', on_delete=models.PROTECT
    )

    # Ozone-depleting potential
    odp = models.FloatField()
    # TODO: any info on when the below two are used?
    min_odp = models.FloatField()
    max_odp = models.FloatField()

    # Global warming potential
    gwp = models.IntegerField(null=True)

    formula = models.CharField(max_length=256)

    number_of_isomers = models.SmallIntegerField(null=True)

    # TODO: what is this?
    gwp2 = models.IntegerField(null=True)

    # Existing data seems to suggest this field is always non-blank,
    # allowing it though just in case...
    carbons = models.CharField(max_length=128, blank=True)

    hydrogens = models.CharField(max_length=128, blank=True)

    fluorines = models.CharField(max_length=128, blank=True)

    chlorines = models.CharField(max_length=128, blank=True)

    bromines = models.CharField(max_length=128, blank=True)

    # Remarks
    remark = models.CharField(max_length=256, blank=True)


class Blend(models.Model):
    """
    Description of blends
    """
    @enum.unique
    class BlendTypes(enum.Enum):
        ZEOTROPE = 'Zeotrope'
        AZEOTROPE = 'Azeotrope'

    blend_id = models.CharField(max_length=64, unique=True)

    # This is a plain-text description of the composition; see `BlendComponent`
    # model for a relational one
    composition = models.CharField(max_length=256)

    other_names = models.CharField(max_length=256, blank=True)

    type = models.CharField(
        max_length=128, choices=((s.value, s.name) for s in BlendTypes)
    )

    odp = models.FloatField(null=True)

    gwp = models.IntegerField(null=True)

    hfc = models.BooleanField(null=True)

    hcfc = models.BooleanField(null=True)

    mp_control = models.CharField(max_length=256, blank=True)

    main_usage = models.CharField(max_length=256, blank=True)

    remark = models.CharField(max_length=256, blank=True)


class BlendComponent(models.Model):
    """
    Model describing the substances composition of each blend
    """
    blend = models.ForeignKey(
        Blend, related_name='components', on_delete=models.PROTECT
    )

    # TODO: 'Ozone Business Data Tables' document *seems* to suggest that
    # the SubstanceRCode should be used instead - any need for that?
    substance = models.ForeignKey(
        Substance, related_name='blends', on_delete=models.PROTECT
    )

    percentage = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
