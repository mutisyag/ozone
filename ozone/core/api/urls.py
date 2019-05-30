from django.urls import re_path, path

from rest_framework_nested import routers

from . import views

# Needed by Django >= 2.0
app_name = "core"


class DefaultRouter(routers.DefaultRouter):
    """
    Extends `DefaultRouter` class to add a method for extending url routes from
    another router.
    """

    def extend(self, added_router):
        """
        Extend the routes with url routes of the passed in router.

        Args:
             router: SimpleRouter instance containing route definitions.
        """
        self.registry.extend(added_router.registry)


router = DefaultRouter()

router.register(r"current-user", views.CurrentUserViewSet, "current_user")

router.register(r"regions", views.RegionViewSet)
router.register(r"subregions", views.SubregionViewSet)
router.register(r"parties", views.PartyViewSet)

router.register(r"periods", views.ReportingPeriodViewSet)
router.register(r"users", views.UserViewSet)
router.register(r"obligations", views.ObligationViewSet)

router.register(r"aggregations", views.AggregationViewSet)
router.register(r"limits", views.LimitViewSet)

# Submissions
submissions_router = routers.SimpleRouter()
submissions_router.register(r"submissions", views.SubmissionViewSet)
router.extend(submissions_router)

# Data reports, info & other stuff that's nested on submissions
questionnaire_router = routers.NestedSimpleRouter(
    submissions_router, "submissions", lookup="submission"
)
questionnaire_router.register(
    "article7-questionnaire",
    views.Article7QuestionnaireViewSet,
    base_name="submission-article7-questionnaire",
)

destructions_router = routers.NestedSimpleRouter(
    submissions_router, "submissions", lookup="submission"
)
destructions_router.register(
    "article7-destructions",
    views.Article7DestructionViewSet,
    base_name="submission-article7-destructions",
)

productions_router = routers.NestedSimpleRouter(
    submissions_router, "submissions", lookup="submission"
)
productions_router.register(
    "article7-productions",
    views.Article7ProductionViewSet,
    base_name="submission-article7-productions"
)

exports_router = routers.NestedSimpleRouter(
    submissions_router, "submissions", lookup="submission"
)
exports_router.register(
    "article7-exports",
    views.Article7ExportViewSet,
    base_name="submission-article7-exports"
)

imports_router = routers.NestedSimpleRouter(
    submissions_router, "submissions", lookup="submission"
)
imports_router.register(
    "article7-imports",
    views.Article7ImportViewSet,
    base_name="submission-article7-imports"
)

nonpartytrades_router = routers.NestedSimpleRouter(
    submissions_router, "submissions", lookup="submission"
)
nonpartytrades_router.register(
    "article7-nonpartytrades",
    views.Article7NonPartyTradeViewSet,
    base_name="submission-article7-nonpartytrades"
)

emissions_router = routers.NestedSimpleRouter(
    submissions_router, "submissions", lookup="submission"
)
emissions_router.register(
    "article7-emissions",
    views.Article7EmissionViewSet,
    base_name="submission-article7-emissions"
)

hat_imports_router = routers.NestedSimpleRouter(
    submissions_router, "submissions", lookup="submission"
)
hat_imports_router.register(
    "hat-imports",
    views.HighAmbientTemperatureImportViewSet,
    base_name="submission-hat-imports"
)

transfers_router = routers.NestedSimpleRouter(
    submissions_router, "submissions", lookup="submission"
)
transfers_router.register(
    "transfers",
    views.TransferViewSet,
    base_name="submission-transfers"
)

submission_transitions_router = routers.NestedSimpleRouter(
    submissions_router, "submissions", lookup="submission"
)
submission_transitions_router.register(
    "submission-transitions",
    views.SubmissionTransitionsViewSet,
    base_name="submission-submission-transitions"
)

submission_info_router = routers.NestedSimpleRouter(
    submissions_router, "submissions", lookup="submission"
)
submission_info_router.register(
    "submission-info",
    views.SubmissionInfoViewSet,
    base_name="submission-submission-info"
)

submission_flags_router = routers.NestedSimpleRouter(
    submissions_router, "submissions", lookup="submission"
)
submission_flags_router.register(
    "submission-flags",
    views.SubmissionFlagsViewSet,
    base_name="submission-submission-flags"
)

submission_remarks_router = routers.NestedSimpleRouter(
    submissions_router, "submissions", lookup="submission"
)
submission_remarks_router.register(
    "submission-remarks",
    views.SubmissionRemarksViewSet,
    base_name="submission-submission-remarks"
)

hat_productions_router = routers.NestedSimpleRouter(
    submissions_router, "submissions", lookup="submission"
)
hat_productions_router.register(
    "hat-productions",
    views.HighAmbientTemperatureProductionViewSet,
    base_name="submission-hat-productions"
)

data_others_router = routers.NestedSimpleRouter(
    submissions_router, "submissions", lookup="submission"
)
data_others_router.register(
    "data-others",
    views.DataOtherViewSet,
    base_name="submission-data-others"
)

submission_files_router = routers.NestedSimpleRouter(
    submissions_router, "submissions", lookup="submission"
)
submission_files_router.register(
    "files",
    views.SubmissionFileViewSet,
    base_name="submission-files"
)

upload_token_router = routers.NestedSimpleRouter(
    submissions_router, "submissions", lookup="submission"
)
upload_token_router.register(
    'token',
    views.UploadTokenViewSet,
    base_name='submission-token'
)

exemption_nomination_router = routers.NestedSimpleRouter(
    submissions_router, "submissions", lookup="submission"
)
exemption_nomination_router.register(
    "exemption-nomination",
    views.ExemptionNominationViewSet,
    base_name="submission-exemption-nomination"
)

exemption_approved_router = routers.NestedSimpleRouter(
    submissions_router, "submissions", lookup="submission"
)
exemption_approved_router.register(
    "exemption-approved",
    views.ExemptionApprovedViewSet,
    base_name="submission-exemption-approved"
)

raf_router = routers.NestedSimpleRouter(
    submissions_router, "submissions", lookup="submission"
)
raf_router.register(
    "raf",
    views.RAFViewSet,
    base_name="submission-raf"
)

email_router = routers.NestedSimpleRouter(
    submissions_router, "submissions", lookup="submission"
)
email_router.register(
    "email",
    views.EmailViewSet,
    base_name="submission-email"
)

nested_routers = [
    questionnaire_router,
    destructions_router,
    productions_router,
    exports_router,
    imports_router,
    nonpartytrades_router,
    emissions_router,
    hat_imports_router,
    hat_productions_router,
    data_others_router,
    transfers_router,
    submission_info_router,
    submission_transitions_router,
    submission_flags_router,
    submission_remarks_router,
    submission_files_router,
    upload_token_router,
    exemption_nomination_router,
    exemption_approved_router,
    raf_router,
    email_router,
]

# Groups
router.register(r"group-substances", views.GroupViewSet)

# Blends
router.register(r"blends", views.BlendViewSet, base_name="blends")

# File uploads
upload_hooks_router = routers.SimpleRouter()
upload_hooks_router.register(
    'uploads',
    views.UploadHookViewSet,
    base_name='uploads'
)
router.extend(upload_hooks_router)

# Authentication
auth_tokens = routers.SimpleRouter()
auth_tokens.register(
    'auth-token',
    views.AuthTokenViewSet,
    base_name='auth-token'
)
router.extend(auth_tokens)

# PDF reports
reports = routers.SimpleRouter()
reports.register(
    'reports',
    views.ReportsViewSet,
    base_name='reports'
)
router.extend(reports)


email_templates = routers.SimpleRouter()
email_templates.register(
    'email-templates',
    views.EmailTemplateViewSet,
    base_name='email-templates'
)
router.extend(email_templates)

urlpatterns = (
    router.urls
    + [url for router in nested_routers for url in router.urls]
    + [
        re_path(
            '^get-non-parties/(?P<period_name>[0-9]+|)',
            views.GetNonPartiesViewSet.as_view(),
            name='get_non_parties',
        ),
        re_path(
            '^get-party-ratifications/(?P<party_id>[0-9]+|)',
            views.PartyRatificationViewSet.as_view(),
            name='get_ratifications',
        ),
        path(
            'default-values/',
            views.DefaultValuesViewSet.as_view(),
            name='default_values'
        ),
        path(
            'get-submission-formats/',
            views.GetSubmissionFormatsViewSet.as_view(),
            name='get_submission_formats'
        ),
    ]
)
