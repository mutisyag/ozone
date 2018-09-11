from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'regions', views.RegionViewSet)
router.register(r'subregions', views.SubregionViewSet)
router.register(r'parties', views.PartyViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls))
]
