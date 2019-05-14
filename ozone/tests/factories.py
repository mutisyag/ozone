from datetime import datetime
from factory import SubFactory, post_generation
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model

from ozone.core.models import (
    Annex,
    Blend,
    Group,
    Meeting,
    Obligation,
    Party,
    PartyType,
    PartyHistory,
    Region,
    ReportingChannel,
    ReportingPeriod,
    Submission,
    SubmissionInfo,
    Subregion,
    Treaty,
    Substance,
    Article7Questionnaire,
    Article7Destruction,
    Article7Production,
    Article7Import,
    Article7Export,
    Article7Emission,
    Article7NonPartyTrade,
    HighAmbientTemperatureProduction,
    HighAmbientTemperatureImport,
    DataOther,
    UploadToken,
    SubmissionFile,
    Language,
    Nomination,
    ExemptionApproved,
    SubmissionFormat,
)

User = get_user_model()


class RegionFactory(DjangoModelFactory):
    abbr = 'TR'
    name = 'Test Region'

    class Meta:
        model = Region


class SubregionFactory(DjangoModelFactory):
    abbr = 'TS'
    name = 'Test Subregion'
    region = SubFactory(RegionFactory)

    class Meta:
        model = Subregion


class PartyFactory(DjangoModelFactory):
    abbr = 'TP'
    name = 'Test Party'
    subregion = SubFactory(SubregionFactory)

    class Meta:
        model = Party


class AnotherPartyFactory(DjangoModelFactory):
    abbr = 'AP'
    name = 'Another Party'
    subregion = SubFactory(SubregionFactory)

    class Meta:
        model = Party


class LanguageEnFactory(DjangoModelFactory):
    language_id = 'E'
    name = 'English'
    iso = 'en'

    class Meta:
        model = Language


class LanguageFrFactory(DjangoModelFactory):
    language_id = 'F'
    name = 'French'
    iso = 'fr'

    class Meta:
        model = Language


class SecretariatUserFactory(DjangoModelFactory):
    is_secretariat = True
    is_superuser = True
    is_staff = True
    is_active = True
    is_read_only = False
    username = 'secretariat'
    email = 'secretariat@example.com'

    class Meta:
        model = User


class SecretariatUserROFactory(DjangoModelFactory):
    is_secretariat = True
    is_superuser = False
    is_staff = True
    is_active = True
    is_read_only = True
    username = 'secretariat_ro'
    email = 'secretariat_ro@example.com'

    class Meta:
        model = User


class ReporterUserFactory(DjangoModelFactory):
    is_secretariat = False
    is_superuser = False
    is_staff = False
    is_active = True
    is_read_only = False
    username = 'reporter'
    email = 'reporter@example.com'

    class Meta:
        model = User


class ReporterUserROFactory(DjangoModelFactory):
    is_secretariat = False
    is_superuser = False
    is_staff = False
    is_active = True
    is_read_only = True
    username = 'reporter_ro'
    email = 'reporter_ro@example.com'

    class Meta:
        model = User


class ReporterUserSamePartyFactory(DjangoModelFactory):
    is_secretariat = False
    is_superuser = False
    is_staff = False
    is_active = True
    is_read_only = False
    username = 'reporter_same_party'
    email = 'reporter_same_party@example.com'

    class Meta:
        model = User


class ReporterUserAnotherPartyFactory(DjangoModelFactory):
    is_secretariat = False
    is_read_only = False
    username = 'reporter_another_party'
    email = 'reporter_another_party@example.com'

    class Meta:
        model = User


class ObligationFactory(DjangoModelFactory):
    name = 'Test Obligation'
    _form_type = 'art7'

    class Meta:
        model = Obligation


class ReportingPeriodFactory(DjangoModelFactory):
    name = '2018'
    start_date = datetime.strptime('2018-01-01', '%Y-%m-%d')
    end_date = datetime.strptime('2018-12-31', '%Y-%m-%d')

    class Meta:
        model = ReportingPeriod


class PartyTypeFactory(DjangoModelFactory):
    abbr = 'A5'
    name = 'Article 5'

    class Meta:
        model = PartyType
        django_get_or_create = ('abbr', 'name',)


class PartyHistoryFactory(DjangoModelFactory):
    population = 10
    is_high_ambient_temperature = False
    is_ceit = False
    is_article5 = True
    is_eu_member = True
    party_type = SubFactory(PartyTypeFactory)

    class Meta:
        model = PartyHistory


class ReportingChannelFactory(DjangoModelFactory):
    name = 'Web form'
    is_default_party = True
    is_default_secretariat = False
    is_default_for_cloning = True

    class Meta:
        model = ReportingChannel


class SubmissionInfoFactory(DjangoModelFactory):
    reporting_officer = 'Test Officer'
    postal_address = 'Test Address'
    email = 'test@officer.net'

    class Meta:
        model = SubmissionInfo


class SubmissionFactory(DjangoModelFactory):
    obligation = SubFactory(ObligationFactory)
    reporting_period = SubFactory(ReportingPeriodFactory)

    @post_generation
    def populate_fields_for_submit(self, *args, **kwargs):
        """
        Automatically called after create() is completed
        """

        # Submission info needs to be properly populated for submit to work
        self.info.reporting_officer = 'Test Officer'
        self.info.postal_address = 'Test Address'
        self.info.email = 'test@officer.net'
        self.info.save()

        if self.filled_by_secretariat:
            self.submitted_at = datetime.strptime('2018-12-31', '%Y-%m-%d')

    @post_generation
    def populate_questionnaire(self, create, extracted, **kwargs):
        # Questionnaire is needed for "Submit" to actually work on Article 7
        # workflows
        if extracted is not False:
            questionnaire = Article7QuestionnaireFactory(submission=self)

    class Meta:
        model = Submission


class MeetingFactory(DjangoModelFactory):
    meeting_id = 'TM'
    location = "Test"
    description = "Test"

    class Meta:
        model = Meeting


class TreatyFactory(DjangoModelFactory):
    treaty_id = 'TT'
    name = 'Test Treaty'
    meeting_id = SubFactory(MeetingFactory)
    date = datetime.strptime('2018-01-01', '%Y-%m-%d')
    entry_into_force_date = datetime.strptime('2020-01-01', '%Y-%m-%d')

    class Meta:
        model = Treaty


class AnnexFactory(DjangoModelFactory):
    annex_id = 'TA'
    name = 'Test Annex'

    class Meta:
        model = Annex


class GroupFactory(DjangoModelFactory):
    group_id = 'TG'
    annex = SubFactory(AnnexFactory)
    name = 'Test Group'

    class Meta:
        model = Group


class BlendFactory(DjangoModelFactory):
    blend_id = 'TB'
    type = 'Zeotrope'
    composition = 'TEST'

    class Meta:
        model = Blend


class SubstanceFactory(DjangoModelFactory):
    name = "Chemical X"
    description = "Don't mix with sugar, spice and everything nice"
    fluorines = "F"
    formula = "CH-XXX"
    group = None
    gwp = 4750
    gwp2 = 6800
    gwp_error_plus_minus = None
    hydrogens = ""
    is_contained_in_polyols = False
    max_odp = 1
    min_odp = 1
    number_of_isomers = 1
    odp = 1
    remark = "See Professor Utonium accident from 1998"
    sort_order = 100
    substance_id = 998

    class Meta:
        model = Substance


class AnotherSubstanceFactory(SubstanceFactory):
    name = "Kryptonite"
    formula = "KRY-XXX"
    substance_id = 997


class Article7QuestionnaireFactory(DjangoModelFactory):
    has_imports = False
    has_exports = False
    has_produced = False
    has_destroyed = False
    has_nonparty = False
    has_emissions = False

    class Meta:
        model = Article7Questionnaire


class DestructionFactory(DjangoModelFactory):
    class Meta:
        model = Article7Destruction


class ProductionFactory(DjangoModelFactory):
    class Meta:
        model = Article7Production


class ImportFactory(DjangoModelFactory):
    class Meta:
        model = Article7Import


class ExportFactory(DjangoModelFactory):
    class Meta:
        model = Article7Export


class EmissionFactory(DjangoModelFactory):
    class Meta:
        model = Article7Emission


class NonPartyTradeFactory(DjangoModelFactory):
    class Meta:
        model = Article7NonPartyTrade


class HighAmbientTemperatureProductionFactory(DjangoModelFactory):
    class Meta:
        model = HighAmbientTemperatureProduction


class HighAmbientTemperatureImportFactory(DjangoModelFactory):
    class Meta:
        model = HighAmbientTemperatureImport


class DataOtherFactory(DjangoModelFactory):
    class Meta:
        model = DataOther


class UploadTokenFactory(DjangoModelFactory):
    class Meta:
        model = UploadToken


class SubmissionFileFactory(DjangoModelFactory):
    class Meta:
        model = SubmissionFile


class NominationFactory(DjangoModelFactory):
    class Meta:
        model = Nomination


class ExemptionApprovedFactory(DjangoModelFactory):
    class Meta:
        model = ExemptionApproved


class SubmissionFormatFactory(DjangoModelFactory):
    name = 'A7 Data forms'

    class Meta:
        model = SubmissionFormat
