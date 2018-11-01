from django.contrib import admin
from django.contrib.auth import get_user_model

from import_export.admin import (
    ImportExportActionModelAdmin,
    ImportExportModelAdmin,
    ImportExportMixin,
)

# Register your models here.
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
from .resources import (
    MeetingResource,
    TreatyResource,
    SubstanceResource,
    PartyResource,
    DecisionResource,
    RegionResource,
    SubregionResource,
    PartyHistoryResource,
    AnnexResource,
    GroupResource,
    BlendResource,
    BlendComponentResource,
    ReportingPeriodResource,
    ObligationResource,
    LanguageResource,
)

User = get_user_model()


# Meeting-related models
@admin.register(Meeting)
class MeetingAdmin(ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin):
    search_fields = ["meeting_id", "description"]
    resource_class = MeetingResource


@admin.register(Treaty)
class TreatyAdmin(ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin):
    search_fields = ["name"]
    resource_class = TreatyResource


@admin.register(Decision)
class DecisionAdmin(ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin):
    search_fields = ["decision_id", "name"]
    resource_class = DecisionResource


# Party-related models
@admin.register(Region)
class RegionAdmin(ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin):
    search_fields = ["abbr", "name"]
    resource_class = RegionResource


@admin.register(Subregion)
class SubregionAdmin(ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin):
    search_fields = ["abbr", "name"]
    resource_class = SubregionResource


@admin.register(Party)
class PartyAdmin(ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'subregion')
    search_fields = ["name"]
    resource_class = PartyResource


@admin.register(PartyHistory)
class PartyHistoryAdmin(
    ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin
):
    list_display = ('party', 'reporting_period')
    search_fields = ["party"]
    resource_class = PartyHistoryResource


@admin.register(Language)
class Language(ImportExportModelAdmin, ImportExportMixin, admin.ModelAdmin):
    search_fields = ["name"]
    resource_class = LanguageResource


# Substance-related models
@admin.register(Annex)
class AnnexAdmin(ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ["name"]
    resource_class = AnnexResource


@admin.register(Group)
class GroupAdmin(ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin):
    search_fields = ["group_id", "annex"]
    resource_class = GroupResource


@admin.register(Substance)
class SubstanceAdmin(ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'group')
    search_fields = ["name"]
    resource_class = SubstanceResource


@admin.register(Blend)
class BlendAdmin(ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin):
    search_fields = ["blend_id"]
    resource_class = BlendResource


@admin.register(BlendComponent)
class BlendComponentAdmin(
    ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin
):
    search_fields = ["blend", "substance"]
    resource_class = BlendComponentResource


# Reporting-related models
@admin.register(ReportingPeriod)
class ReportingPeriodAdmin(
    ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin
):
    search_fields = ["name"]
    resource_class = ReportingPeriodResource


@admin.register(Obligation)
class ObligationAdmin(
    ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin
):
    search_fields = ["name"]
    resource_class = ObligationResource


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ["username", "first_name", "last_name"]
