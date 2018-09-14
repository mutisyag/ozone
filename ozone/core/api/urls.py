from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'regions', views.RegionViewSet)
router.register(r'subregions', views.SubregionViewSet)
router.register(r'parties', views.PartyViewSet)

router.register(r'periods', views.ReportingPeriodViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'obligations', views.ObligationViewSet)

router.register(r'submissions', views.SubmissionViewSet)

router.register(r'article7questionnaires', views.Article7QuestionnaireViewSet)
router.register(r'article7destructions', views.Article7DestructionViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls))
]
