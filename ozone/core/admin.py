import uuid

import adminactions.actions as actions

from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter
from django.contrib import admin, messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import logout as auth_logout
from django.contrib.admin import AdminSite
from django.contrib.admin import site
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import F, Subquery
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
    Region,
    Subregion,
    MDGRegion,
    Party,
    PartyHistory,
    ReportingPeriod,
    Obligation,
    Annex,
    Group,
    Substance,
    Blend,
    BlendComponent,
    Submission,
    SubmissionInfo,
    ReportingChannel,
    SubmissionFormat,
    BaselineType,
    ControlMeasure,
    Baseline,
    Limit,
    PartyRatification,
    PartyDeclaration,
    CriticalUseCategory,
    FormTypes,
    Transfer,
    Email,
    EmailTemplate,
    ProcessAgentApplication,
    ProcessAgentContainTechnology,
    ProcessAgentEmissionLimit,
    ProcessAgentUsesReported,
    ProcessAgentApplicationValidity,
    ProcessAgentEmissionLimitValidity,
    Decision,
    DeviationType,
    DeviationSource,
    PlanOfActionDecision,
    PlanOfAction,
    ProdCons,
    ProdConsMT,
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


def custom_title_dropdown_filter(title):
    class Wrapper(DropdownFilter):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.title = title
    return Wrapper


# Meeting-related models
@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('meeting_id', 'description', 'location', 'start_date', 'end_date')
    list_filter = ('treaty_flag',)
    search_fields = ['meeting_id', 'description', 'location']


@admin.register(Treaty)
class TreatyAdmin(admin.ModelAdmin):
    list_display = ('name', 'meeting_id', 'date', 'entry_into_force_date')


# Party-related models
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbr')


@admin.register(MDGRegion)
class MDGRegionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'income_type', 'get_parent_regions', 'get_child_regions')
    search_fields = ['code', 'name']

    def get_parent_regions(self, obj):
        return ', '.join(x.name for x in obj.parent_regions.all())
    get_parent_regions.short_description = 'Parents'

    def get_child_regions(self, obj):
        return ', '.join(x.name for x in obj.child_regions.all())
    get_child_regions.short_description = 'Children'


@admin.register(Subregion)
class SubregionAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbr', 'region')
    list_filter = ('region',)
    search_fields = ["abbr", "name"]


class MainPartyFilter(RelatedDropdownFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lookup_choices = Party.objects.filter(
            parent_party__id=F('id'),
        ).order_by('name').values_list('id', 'name')


class ParentPartyFilter(RelatedDropdownFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lookup_choices = Party.objects.filter(
            id__in=Subquery(Party.objects.exclude(
                parent_party__id=F('id'),
            ).values('parent_party_id'))
        ).order_by('name').values_list('id', 'name')


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbr', 'subregion', 'parent_party')
    list_filter = (
        'subregion__region', 'subregion',
        ('parent_party', ParentPartyFilter)
    )
    search_fields = ['name', 'abbr']


@admin.register(PartyHistory)
class PartyHistoryAdmin(admin.ModelAdmin):
    list_display = ('party', 'reporting_period', 'party_type')
    list_filter = (
        'party_type',
        ('reporting_period__name', custom_title_dropdown_filter('period')),
        ('party', MainPartyFilter),
    )
    search_fields = ["party__name"]


# Substance-related models
@admin.register(Annex)
class AnnexAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('group_id', 'name', 'description', 'name_alt', 'description_alt', 'control_treaty', 'report_treaty')
    list_filter = ('annex', 'control_treaty', 'report_treaty')


@admin.register(Substance)
class SubstanceAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'group', 'description', 'odp', 'gwp',
        'formula', 'number_of_isomers', 'sort_order',
    )
    list_filter = ('group', 'is_contained_in_polyols', 'is_captured', 'has_critical_uses')
    search_fields = ['name', 'description', 'substance_id']


@admin.register(Blend)
class BlendAdmin(admin.ModelAdmin):
    list_display = (
        'blend_id', 'composition',
        'type', 'party', 'odp', 'gwp',
        'trade_name', 'sort_order',
    )
    list_filter = (
        'type',
        ('party', MainPartyFilter),
    )
    search_fields = ['blend_id', 'legacy_blend_id']


@admin.register(BlendComponent)
class BlendComponentAdmin(admin.ModelAdmin):
    list_display = ('blend', 'substance', 'percentage')
    search_fields = ['blend__blend_id', 'substance__name']
    list_filter = (
        ('blend__blend_id', DropdownFilter),
        'blend__type',
    )


# Reporting-related models
@admin.register(ReportingPeriod)
class ReportingPeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'description')
    search_fields = ["name"]
    list_filter = (
        'is_reporting_open', 'is_reporting_allowed',
    )
    ordering = ('-end_date',)


@admin.register(Obligation)
class ObligationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_default', 'is_active')
    exclude = ('has_reporting_periods',)
    readonly_fields = ['_form_type']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    base_list_display = (
        "username", "first_name", "last_name", "email", "is_secretariat", "is_read_only", "party",
        "is_active", "activated", "last_login",
    )
    superuser_list_display = (
        "login_as",
    )
    search_fields = ["username", "first_name", "last_name"]
    actions = ["reset_password"]
    exclude = ["password", "user_permissions"]
    readonly_fields = ["last_login", "date_joined", "created_by", "activated"]
    list_filter = (
        ("party", MainPartyFilter),
        "is_secretariat", "is_read_only", "is_staff", "is_superuser",
        "is_active", "activated",
    )

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


def _build_getter(prefix, name):
    def get_boolean(obj):
        return getattr(obj, prefix + name)
    get_boolean.short_description = name.upper()
    get_boolean.boolean = True
    return get_boolean


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):

    def __getattr__(self, name):
        return _build_getter('flag_has_reported_', name)

    list_display = (
        '__str__', 'party', 'reporting_period', 'obligation', '_current_state',
        'flag_provisional', 'flag_valid', 'flag_superseded',
        'flag_checked_blanks', 'flag_has_blanks', 'flag_confirmed_blanks',
        'flag_emergency', 'flag_approved',
        'a1', 'a2', 'b1', 'b2', 'b3', 'c1', 'c2', 'c3', 'e', 'f',
    )
    list_filter = (
        'obligation',
        ('reporting_period__name', custom_title_dropdown_filter('period')),
        ('party', MainPartyFilter),
        '_current_state',
        'flag_provisional', 'flag_valid', 'flag_superseded',
        'flag_checked_blanks', 'flag_has_blanks', 'flag_confirmed_blanks',
        'flag_emergency', 'flag_approved',
        'flag_has_reported_a1', 'flag_has_reported_a2',
        'flag_has_reported_b1', 'flag_has_reported_b2', 'flag_has_reported_b3',
        'flag_has_reported_c1', 'flag_has_reported_c2', 'flag_has_reported_c3',
        'flag_has_reported_e',
        'flag_has_reported_f'
    )
    search_fields = ['party__name']

    def get_readonly_fields(self, request, obj=None):
        self.readonly_fields = []
        for field in self.model._meta.fields:
            if 'flag' not in field.name and 'state' not in field.name:
                self.readonly_fields.append(field.name)
        return self.readonly_fields

    def get_deleted_objects(self, objs, request):
        deletable_objects, model_count, perms_needed, protected = super(
            SubmissionAdmin, self
        ).get_deleted_objects(objs, request)
        protected = False
        return deletable_objects, model_count, perms_needed, protected

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj._current_state = 'data_entry'
            obj.save()
            obj.delete()

    def delete_model(self, request, obj):
        obj._current_state = 'data_entry'
        obj.save()
        obj.delete()


@admin.register(SubmissionInfo)
class SubmissionInfoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'reporting_officer', 'country', 'date')
    list_filter = (
        'submission_format',
        'submission__obligation',
        ('submission__reporting_period__name', custom_title_dropdown_filter('period')),
        ('submission__party', MainPartyFilter)
    )
    search_fields = ('submission__party__name',)
    readonly_fields = ('submission', )


@admin.register(ReportingChannel)
class ReportingChannelAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'description',
        'is_default_party', 'is_default_secretariat', 'is_default_for_cloning',
    )


@admin.register(SubmissionFormat)
class SubmissionFormatAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_default_party')


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
    list_filter = ('group', 'baseline_type', ('party', MainPartyFilter))
    search_fields = ["party__name"]


@admin.register(Limit)
class LimitAdmin(admin.ModelAdmin):
    list_display = (
        'party', 'group', 'reporting_period', 'limit_type', 'limit',
    )
    list_filter = (
        'group', 'limit_type',
        ('reporting_period__name', custom_title_dropdown_filter('period')),
        ('party', MainPartyFilter)
    )
    search_fields = ['party__name', 'party__abbr']


@admin.register(PartyRatification)
class PartyRatificationAdmin(admin.ModelAdmin):
    list_display = ('party', 'treaty', 'ratification_type', 'ratification_date', 'entry_into_force_date')
    list_filter = (('party', MainPartyFilter), 'treaty', 'ratification_type')
    search_fields = ['party__name', 'treaty__name']


@admin.register(PartyDeclaration)
class PartyDeclarationAdmin(admin.ModelAdmin):
    list_display = ('party', )
    list_filter = (('party', MainPartyFilter),)
    search_fields = ['party__name', 'declaration']
    ordering = ('party__name', )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        main_parties_queryset = Party.objects.filter(
            parent_party__id=F('id'),
        ).order_by('name')
        form.base_fields['party'].queryset = main_parties_queryset
        return form


@admin.register(CriticalUseCategory)
class CriticalUseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ['name']


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = (
        'reporting_period', 'source_party', 'destination_party', 'substance', 'transferred_amount',
    )
    list_filter = (
        ('source_party', MainPartyFilter),
        ('destination_party', MainPartyFilter),
        ('reporting_period__name', custom_title_dropdown_filter('period')),
        ('substance__name', custom_title_dropdown_filter('substance')),
    )
    search_fields = (
        'source_party__name', 'destination_party__name', 'substance__name'
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        main_parties_queryset = Party.objects.filter(
            parent_party__id=F('id'),
        ).order_by('name')
        source_sub_queryset = dest_sub_queryset = Submission.objects.filter(
            obligation___form_type=FormTypes.TRANSFER.value
        ).order_by('reporting_period__name')
        if obj is not None:
            source_sub_queryset = source_sub_queryset.filter(
                party=obj.source_party
            )
            dest_sub_queryset = dest_sub_queryset.filter(
                party=obj.destination_party
            )
        form.base_fields['source_party_submission'].queryset = source_sub_queryset
        form.base_fields['destination_party_submission'].queryset = dest_sub_queryset
        form.base_fields['source_party'].queryset = main_parties_queryset
        form.base_fields['destination_party'].queryset = main_parties_queryset
        return form


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('date', 'subject', 'to', 'submission')
    list_filter = (
        ('submission__reporting_period__name', custom_title_dropdown_filter('period')),
        ('submission__party', MainPartyFilter),
    )


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', )
    search_fields = ['name', 'subject', 'description', ]


@admin.register(ProcessAgentApplication)
class ProcessAgentApplicationAdmin(admin.ModelAdmin):
    list_display = ('validity', 'counter', 'substance', 'application')
    list_filter = (
        ('substance__name', custom_title_dropdown_filter('substance')),
        (
            'validity__decision__decision_id',
            custom_title_dropdown_filter('decision')
        ),
        ('counter', custom_title_dropdown_filter('counter'))
    )
    search_fields = ('validity', 'substance__name')


@admin.register(ProcessAgentEmissionLimit)
class ProcessAgentEmissionLimitAdmin(admin.ModelAdmin):
    list_display = ('party', 'validity', 'makeup_consumption', 'max_emissions')
    list_filter = (
        ('party', MainPartyFilter),
    )
    search_fields = ('party__name', 'validity')


class ProcessAgentBaseAdmin:
    def get_reporting_period(self, obj):
        return obj.submission.reporting_period
    get_reporting_period.short_description = 'Reporting period'

    def get_party(self, obj):
        return obj.submission.party
    get_party.short_description = 'Party'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        submission_queryset = Submission.objects.filter(
            obligation___form_type=FormTypes.PROCAGENT.value
        ).order_by('reporting_period__name')
        form.base_fields['submission'].queryset = submission_queryset
        return form


@admin.register(ProcessAgentContainTechnology)
class ProcessAgentContainTechnologyAdmin(admin.ModelAdmin):
    list_display = ('description',)
    search_fields = ('description',)


@admin.register(ProcessAgentUsesReported)
class ProcessAgentUsesReportedAdmin(ProcessAgentBaseAdmin, admin.ModelAdmin):
    def get_application(self, obj):
        return obj.application.application if obj.application else ''
    get_application.short_description = 'Application'

    list_display = (
        'get_reporting_period', 'get_party', 'get_application',
        'makeup_quantity', 'emissions', 'units'
    )
    list_filter = (
        (
            'submission__reporting_period__name',
            custom_title_dropdown_filter('period')
        ),
        ('submission__party', MainPartyFilter)
    )
    search_fields = (
        'submission__reporting_period__name', 'submission__party__name',
    )


@admin.register(ProcessAgentApplicationValidity)
class ProcessAgentApplicationValidityAdmin(admin.ModelAdmin):
    list_display = ('decision', 'start_date', 'end_date')
    search_fields = ('decision', )


@admin.register(ProcessAgentEmissionLimitValidity)
class ProcessAgentEmissionLimitValidityAdmin(admin.ModelAdmin):
    list_display = ('decision', 'start_date', 'end_date')
    search_fields = ('decision', )


@admin.register(Decision)
class DecisionAdmin(admin.ModelAdmin):
    list_display = ('decision_id', 'name', 'meeting')
    search_fields = ('decision_id', 'name')
    list_filter = (
        ('meeting__description', custom_title_dropdown_filter('meeting')),
    )


@admin.register(DeviationType)
class DeviationTypeAdmin(admin.ModelAdmin):
    list_display = ('deviation_type_id', 'description', 'deviation_pc')
    search_fields = ('deviation_type_id', 'deviation_pc')


@admin.register(DeviationSource)
class DeviationSourceAdmin(admin.ModelAdmin):
    list_display = (
        'party', 'reporting_period', 'group', 'deviation_type',
        'production', 'consumption'
    )
    search_fields = (
        'reporting_period__name', 'party__name',
        'deviation_type__deviation_type_id'
    )
    list_filter = (
        ('party', MainPartyFilter),
        ('reporting_period__name', custom_title_dropdown_filter('Period')),
        'group'
    )


@admin.register(PlanOfActionDecision)
class PlanOfActionDecisionAdmin(admin.ModelAdmin):
    list_display = ('decision', 'party', 'year_adopted')
    search_fields = ('decision', 'party__name', 'year_adopted')
    list_filter = (
        ('party', MainPartyFilter),
    )


@admin.register(PlanOfAction)
class PlanOfActionAdmin(admin.ModelAdmin):
    list_display = (
        'party', 'reporting_period', 'group', 'benchmark',
        'annex_group_description', 'combined_id', 'is_valid', 'decision',
    )
    search_fields = (
        'reporting_period__name', 'party__name', 'group__group_id',
    )
    list_filter = (
        ('reporting_period__name', custom_title_dropdown_filter('Period')),
        ('party', MainPartyFilter),
        'group'
    )


@admin.register(ProdCons)
class ProdConsAdmin(admin.ModelAdmin):
    list_display = (
        'party', 'reporting_period', 'group',
        'calculated_production', 'calculated_consumption',
        'baseline_prod', 'baseline_cons', 'limit_prod', 'limit_cons'
    )
    list_filter = (
        ('reporting_period__name', custom_title_dropdown_filter('Period')),
        ('party', MainPartyFilter),
        'group'
    )


@admin.register(ProdConsMT)
class ProdConsMTAdmin(admin.ModelAdmin):
    def get_group(self, obj):
        return obj.substance.group
    get_group.short_description = 'Group'

    list_display = (
        'party', 'reporting_period', 'get_group', 'substance',
        'calculated_production', 'calculated_consumption'
    )
    list_filter = (
        ('reporting_period__name', custom_title_dropdown_filter('Period')),
        ('party', MainPartyFilter),
        ('substance__name', custom_title_dropdown_filter('substance')),
        'substance__group'
    )


# register all adminactions
actions.add_to_site(site)
