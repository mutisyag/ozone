import uuid

from django.contrib import admin, messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import logout as auth_logout
from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from django.views.decorators.cache import never_cache
from rest_framework.authtoken.models import Token
from django.utils.translation import gettext_lazy as _

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
    Submission,
    SubmissionInfo,
    ReportingChannel,
    SubmissionFormat,
    BaselineType,
    ControlMeasure,
    Baseline,
    Limit,
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
    SubmissionResource,
    SubmissionInfoResource,
    ReportingChannelResource,
    SubmissionFormatResource,
    BaselineTypeResource,
    ControlMeasureResource,
    BaselineResource,
    LimitResource,
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


class OzoneAuthenticationForm(AuthenticationForm):
    """Custom auth form, that allows non-staff users as well."""
    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': _(
            "Please enter the correct %(username)s and password for the "
            "account. Note that both fields may be case-sensitive."
        ),
    }
    required_css_class = 'required'


# For some reason this is instantiated twice, somewhere (!?)
# Make it singleton.

class OzoneAdminSite(AdminSite, metaclass=Singleton):
    """Custom admin site"""
    login_form = OzoneAuthenticationForm

    # Text to put at the end of each page's <title>.
    site_title = _('ORS')

    # Text to put in each page's <h1>.
    site_header = _('Ozone Reporting System')

    # Text to put at the top of the admin index page.
    index_title = _('Administration')

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

    @never_cache
    def index(self, request, extra_context=None):
        """Override to prevent infinite redirects."""
        response = super(OzoneAdminSite, self).index(request, extra_context=extra_context)
        if request.user.is_active and not request.user.is_staff:
            # This doesn't work on development.
            return redirect("/")
        return response

    def has_permission(self, request):
        """Override, and remove the is_staff condition. Each resource is
        protected individually, except for the index page.
        """
        return request.user.is_active


# Meeting-related models
@admin.register(Meeting)
class MeetingAdmin(ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin):
    list_display = ('meeting_id', 'description', 'location', 'start_date', 'end_date')
    search_fields = ["meeting_id", "description"]
    resource_class = MeetingResource


@admin.register(Treaty)
class TreatyAdmin(ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'meeting_id', 'date', 'entry_into_force_date')
    resource_class = TreatyResource


# Party-related models
@admin.register(Region)
class RegionAdmin(ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'abbr')
    resource_class = RegionResource


@admin.register(Subregion)
class SubregionAdmin(ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'abbr')
    list_filter = ('region',)
    search_fields = ["abbr", "name"]
    resource_class = SubregionResource


@admin.register(Party)
class PartyAdmin(ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'abbr', 'subregion')
    list_filter = ('subregion',)
    search_fields = ['name', 'abbr']
    resource_class = PartyResource


@admin.register(PartyHistory)
class PartyHistoryAdmin(
    ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin
):
    list_display = ('party', 'reporting_period', 'party_type')
    list_filter = ('party_type', 'reporting_period')
    search_fields = ["party__name"]
    resource_class = PartyHistoryResource


# Substance-related models
@admin.register(Annex)
class AnnexAdmin(ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'description')
    resource_class = AnnexResource


@admin.register(Group)
class GroupAdmin(ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin):
    list_display = ('group_id', 'name', 'description')
    list_filter = ('annex', 'control_treaty', 'report_treaty')
    resource_class = GroupResource


@admin.register(Substance)
class SubstanceAdmin(ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'group', 'description')
    list_filter = ('group',)
    search_fields = ['name', 'description']
    resource_class = SubstanceResource


@admin.register(Blend)
class BlendAdmin(ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin):
    list_display = ('blend_id', 'composition', 'type')
    list_filter = ('type',)
    search_fields = ['blend_id']
    resource_class = BlendResource


@admin.register(BlendComponent)
class BlendComponentAdmin(
    ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin
):
    list_display = ('blend', 'substance', 'percentage')
    search_fields = ['blend__blend_id', 'substance__name']
    resource_class = BlendComponentResource


# Reporting-related models
@admin.register(ReportingPeriod)
class ReportingPeriodAdmin(
    ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin
):
    list_display = ('name', 'start_date', 'end_date')
    search_fields = ["name"]
    resource_class = ReportingPeriodResource


@admin.register(Obligation)
class ObligationAdmin(
    ImportExportActionModelAdmin, ImportExportMixin, admin.ModelAdmin
):
    list_display = ('name',)
    readonly_fields = ['_form_type']
    resource_class = ObligationResource


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    base_list_display = (
        "username", "first_name", "last_name", "email", "is_secretariat", "is_read_only", "party",
    )
    superuser_list_display = (
        "login_as",
    )
    search_fields = ["username", "first_name", "last_name"]
    actions = ["reset_password"]
    exclude = ["password"]
    readonly_fields = ["last_login", "date_joined", "created_by", "activated"]

    def reset_password(self, request, queryset, template="password_reset"):
        domain_override = request.META.get("HTTP_HOST")
        use_https = request.environ.get("wsgi.url_scheme", "https").lower() == "https"
        users = []

        body = f"registration/{template}_email.html"
        subject = f"registration/{template}_subject.txt"

        for user in queryset:
            form = PasswordResetForm({'email': user.email})
            form.full_clean()
            form.save(
                domain_override=domain_override, use_https=use_https, email_template_name=body,
                subject_template_name=subject,
            )
            users.append(user.username)
        if len(users) > 10:
            self.message_user(request, _("Email sent to %d users for password reset") % len(users),
                              level=messages.SUCCESS)
        else:
            self.message_user(request, _("Email sent to %s for password reset") % ", ".join(users),
                              level=messages.SUCCESS)
    reset_password.short_description = _("Reset user password")

    def login_as(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('impersonate-start', kwargs={"uid": obj.id}),
            _('Login'),
        )

    def get_list_display(self, request):
        if request.user.is_superuser:
            return self.base_list_display + self.superuser_list_display

        return self.base_list_display

    def save_model(self, request, obj, form, change):
        if not change:
            # Set a random password for the new user
            # The user will need to set a new password
            obj.password = str(uuid.uuid4())
            obj.created_by = request.user
            # The user is inactive until a password is set
            obj.activated = False
        super(UserAdmin, self).save_model(request, obj, form, change)
        if not change:
            self.reset_password(request, [obj], template="account_created")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'party', 'reporting_period', 'obligation')
    list_filter = ('obligation', 'reporting_period', 'party')
    search_fields = ['party__name']
    resource_class = SubmissionResource

    def get_readonly_fields(self, request, obj=None):
        self.readonly_fields = []
        for field in self.model._meta.fields:
            if 'flag' not in field.name and 'state' not in field.name:
                self.readonly_fields.append(field.name)
        return self.readonly_fields


@admin.register(SubmissionInfo)
class SubmissionInfoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'reporting_officer', 'country', 'date')
    list_filter = (
        'submission_format',
        'submission__obligation',
        'submission__reporting_period',
        'submission__party'
    )
    search_fields = ('submission__party__name',)
    resource_class = SubmissionInfoResource


@admin.register(ReportingChannel)
class ReportingChannelAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'description',
        'is_default_party', 'is_default_secretariat', 'is_default_for_cloning',
    )
    resource_class = ReportingChannelResource


@admin.register(SubmissionFormat)
class SubmissionFormatAdmin(admin.ModelAdmin):
    resource_class = SubmissionFormatResource


@admin.register(BaselineType)
class BaselineTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'remarks')
    resource_class = BaselineTypeResource


@admin.register(ControlMeasure)
class ControlMeasureAdmin(admin.ModelAdmin):
    list_display = (
        'group', 'party_type', 'limit_type', 'baseline_type', 'start_date', 'end_date', 'allowed',
    )
    list_filter = ('group', 'party_type', 'limit_type', 'baseline_type')
    resource_class = ControlMeasureResource


@admin.register(Baseline)
class BaselineAdmin(admin.ModelAdmin):
    list_display = (
        'party', 'group', 'baseline_type', 'baseline',
    )
    list_filter = ('group', 'baseline_type', 'party')
    search_fields = ["party__name"]
    resource_class = BaselineResource


@admin.register(Limit)
class LimitAdmin(admin.ModelAdmin):
    list_display = (
        'party', 'group', 'reporting_period', 'limit_type', 'limit',
    )
    list_filter = ('group', 'limit_type', 'reporting_period', 'party')
    search_fields = ['party__name', 'party__abbr']
    resource_class = LimitResource
