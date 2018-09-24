from import_export import resources
from .models import (
    Meeting,
    Treaty,
    Decision,
    Region,
    Subregion,
    Party,
    PartyHistory,
    ReportingPeriod,
    Obligation,
    Annex,
    Group,
    Substance,
    Blend,
    BlendComponent,
    Language,
)


class MeetingResource(resources.ModelResource):
    class Meta:
        model = Meeting


class TreatyResource(resources.ModelResource):
    class Meta:
        model = Treaty


class DecisionResource(resources.ModelResource):
    class Meta:
        model = Decision


class RegionResource(resources.ModelResource):
    class Meta:
        model = Region


class SubregionResource(resources.ModelResource):
    class Meta:
        model = Subregion


class PartyResource(resources.ModelResource):
    class Meta:
        model = Party


class LanguageResource(resources.ModelResource):
    class Meta:
        model = Language


class PartyHistoryResource(resources.ModelResource):
    class Meta:
        model = PartyHistory


class AnnexResource(resources.ModelResource):
    class Meta:
        model = Annex


class GroupResource(resources.ModelResource):
    class Meta:
        model = Group


class SubstanceResource(resources.ModelResource):
    class Meta:
        model = Substance


class BlendResource(resources.ModelResource):
    class Meta:
        model = Blend


class BlendComponentResource(resources.ModelResource):
    class Meta:
        model = BlendComponent


class ReportingPeriodResource(resources.ModelResource):
    class Meta:
        model = ReportingPeriod


class ObligationResource(resources.ModelResource):
    class Meta:
        model = Obligation
