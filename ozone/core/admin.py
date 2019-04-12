import uuid

import adminactions.actions as actions

from django_admin_listfilter_dropdown.filters import DropdownFilter
from django.contrib import admin, messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import logout as auth_logout
from django.contrib.admin import AdminSite
from django.contrib.admin import site
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from django.views.decorators.cache import never_cache
from rest_framework.authtoken.models import Token
from django.utils.translation import gettext_lazy as _

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
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('meeting_id', 'description', 'location', 'start_date', 'end_date')
    search_fields = ["meeting_id", "description"]


@admin.register(Treaty)
class TreatyAdmin(admin.ModelAdmin):
    list_display = ('name', 'meeting_id', 'date', 'entry_into_force_date')


# Party-related models
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbr')


@admin.register(Subregion)
class SubregionAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbr')
    list_filter = ('region',)
    search_fields = ["abbr", "name"]


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbr', 'subregion')
    list_filter = ('subregion',)
    search_fields = ['name', 'abbr']


@admin.register(PartyHistory)
class PartyHistoryAdmin(admin.ModelAdmin):
    list_display = ('party', 'reporting_period', 'party_type')
    list_filter = ('party_type', ('reporting_period__name', DropdownFilter))
    search_fields = ["party__name"]


# Substance-related models
@admin.register(Annex)
class AnnexAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('group_id', 'name', 'description')
    list_filter = ('annex', 'control_treaty', 'report_treaty')


@admin.register(Substance)
class SubstanceAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'description')
    list_filter = ('group',)
    search_fields = ['name', 'description']


@admin.register(Blend)
class BlendAdmin(admin.ModelAdmin):
    list_display = ('blend_id', 'composition', 'type')
    list_filter = ('type',)
    search_fields = ['blend_id']


@admin.register(BlendComponent)
class BlendComponentAdmin(admin.ModelAdmin):
    list_display = ('blend', 'substance', 'percentage')
    search_fields = ['blend__blend_id', 'substance__name']


# Reporting-related models
@admin.register(ReportingPeriod)
class ReportingPeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    search_fields = ["name"]


@admin.register(Obligation)
class ObligationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    readonly_fields = ['_form_type']


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
    list_filter = (
        'obligation',
        ('reporting_period__name', DropdownFilter),
        ('party__name', DropdownFilter)
    )
    search_fields = ['party__name']

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
        ('submission__reporting_period__name', DropdownFilter),
        ('submission__party__name', DropdownFilter)
    )
    search_fields = ('submission__party__name',)


@admin.register(ReportingChannel)
class ReportingChannelAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'description',
        'is_default_party', 'is_default_secretariat', 'is_default_for_cloning',
    )


@admin.register(SubmissionFormat)
class SubmissionFormatAdmin(admin.ModelAdmin):
    pass

@admin.register(BaselineType)
class BaselineTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'remarks')


@admin.register(ControlMeasure)
class ControlMeasureAdmin(admin.ModelAdmin):
    list_display = (
        'group', 'party_type', 'limit_type', 'baseline_type', 'start_date', 'end_date', 'allowed',
    )
    list_filter = ('group', 'party_type', 'limit_type', 'baseline_type')


@admin.register(Baseline)
class BaselineAdmin(admin.ModelAdmin):
    list_display = (
        'party', 'group', 'baseline_type', 'baseline',
    )
    list_filter = ('group', 'baseline_type', ('party__name', DropdownFilter))
    search_fields = ["party__name"]


@admin.register(Limit)
class LimitAdmin(admin.ModelAdmin):
    list_display = (
        'party', 'group', 'reporting_period', 'limit_type', 'limit',
    )
    list_filter = (
        'group', 'limit_type',
        ('reporting_period__name', DropdownFilter),
        ('party__name', DropdownFilter)
    )
    search_fields = ['party__name', 'party__abbr']

# register all adminactions
actions.add_to_site(site)
