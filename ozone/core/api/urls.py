from django.conf.urls import url, include
from rest_framework_nested import routers

from . import views

# Needed by Django >= 2.0
app_name = 'core'


class DefaultRouter(routers.DefaultRouter):
    """
    Extends `DefaultRouter` class to add a method for extending url routes from another router.
    """
    def extend(self, router):
        """
        Extend the routes with url routes of the passed in router.

        Args:
             router: SimpleRouter instance containing route definitions.
        """
        self.registry.extend(router.registry)


router = DefaultRouter()

router.register(r"regions", views.RegionViewSet)
router.register(r"subregions", views.SubregionViewSet)
router.register(r"parties", views.PartyViewSet)

router.register(r"periods", views.ReportingPeriodViewSet)
router.register(r"users", views.UserViewSet)
router.register(r"obligations", views.ObligationViewSet)

# Submissions
submissions_router = routers.SimpleRouter()
submissions_router.register(r'submissions', views.SubmissionViewSet)
router.extend(submissions_router)

# Data reports, nested on submissions
destructions_router = routers.NestedSimpleRouter(
    submissions_router, 'submissions', lookup='submission'
)
destructions_router.register(
    'article7-destructions',
    views.Article7DestructionViewSet,
    base_name='submission-article7-destruction'
)
#router.register(r"article7questionnaires", views.Article7QuestionnaireViewSet)

nested_routers = [destructions_router, ]

urlpatterns = router.urls + [url for router in nested_routers for url in router.urls]
