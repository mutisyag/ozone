from django.contrib import admin
from django.contrib.auth import logout as auth_logout
from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.cache import never_cache
from rest_framework.authtoken.models import Token

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


class Singleton(type):
    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


# For some reason this is instantiated twice, somewhere (!?)
# Make it singleton.

class OzoneAdminSite(AdminSite, metaclass=Singleton):
    @never_cache
    def login(self, request, extra_context=None):
        response = super(OzoneAdminSite, self).login(request, extra_context=extra_context)
        if request.user.is_authenticated:
            # Set authToken cookie, this is also used by the FrontEnd app
            token, created = Token.objects.get_or_create(user=request.user)
            if request.GET.get('next'):
                response = redirect(request.GET.get('next'))
            response.set_cookie("authToken", token.key)
        return response

    @never_cache
    def logout(self, request, extra_context=None):
        auth_logout(request)
        response = redirect(reverse("admin:login"))
        response.delete_cookie("authToken")
        return response


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
