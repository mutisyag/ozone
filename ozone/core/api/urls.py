from rest_framework_nested import routers

from . import views

# Needed by Django >= 2.0
app_name = "core"


class DefaultRouter(routers.DefaultRouter):
    """
    Extends `DefaultRouter` class to add a method for extending url routes from another router.
    """

    def extend(self, added_router):
        """
        Extend the routes with url routes of the passed in router.

        Args:
             router: SimpleRouter instance containing route definitions.
        """
        self.registry.extend(added_router.registry)


router = DefaultRouter()

router.register(r"regions", views.RegionViewSet)
router.register(r"subregions", views.SubregionViewSet)
router.register(r"parties", views.PartyViewSet)

router.register(r"periods", views.ReportingPeriodViewSet)
router.register(r"users", views.UserViewSet)
router.register(r"obligations", views.ObligationViewSet)

# Submissions
submissions_router = routers.SimpleRouter()
submissions_router.register(r"submissions", views.SubmissionViewSet)
router.extend(submissions_router)

# Data reports, nested on submissions
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

nested_routers = [
    questionnaire_router,
    destructions_router,
    productions_router,
    exports_router,
    nonpartytrades_router,
    emissions_router,
]

# Groups
groups_router = routers.SimpleRouter()
groups_router.register(r"group-substances", views.GroupViewSet)
router.extend(groups_router)


urlpatterns = router.urls + [url
                             for router in nested_routers
                             for url in router.urls]
