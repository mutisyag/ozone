from datetime import datetime
from factory import SubFactory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model

from ozone.core.models import (
    Obligation,
    Party,
    Region,
    ReportingChannel,
    ReportingPeriod,
    Submission,
    Subregion,
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


class SecretariatUserFactory(DjangoModelFactory):
    is_secretariat = True
    is_read_only = False
    username = 'secretariat'
    email = 'secretariat@example.com'

    class Meta:
        model = User


class SecretariatUserROFactory(DjangoModelFactory):
    is_secretariat = True
    is_read_only = True
    username = 'secretariat_ro'
    email = 'secretariat_ro@example.com'

    class Meta:
        model = User


class ReporterUserFactory(DjangoModelFactory):
    is_secretariat = False
    is_read_only = False
    username = 'reporter'
    email = 'reporter@example.com'

    class Meta:
        model = User


class ReporterUserSamePartyFactory(DjangoModelFactory):
    is_secretariat = False
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

    class Meta:
        model = Obligation


class ReportingPeriodFactory(DjangoModelFactory):
    name = '2018'
    start_date = datetime.strptime('2018-01-01', '%Y-%m-%d')
    end_date = datetime.strptime('2018-12-31', '%Y-%m-%d')

    class Meta:
        model = ReportingPeriod


class ReportingChannelFactory(DjangoModelFactory):
    name = 'Web form'

    class Meta:
        model = ReportingChannel


class SubmissionFactory(DjangoModelFactory):
    obligation = SubFactory(ObligationFactory)
    reporting_period = SubFactory(ReportingPeriodFactory)

    class Meta:
        model = Submission
