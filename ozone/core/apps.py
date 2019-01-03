from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class CoreConfig(AppConfig):
    name = 'ozone.core'
    verbose_name = "Ozone Reporting Core"


class OzoneAdminConfig(AdminConfig):
    default_site = "ozone.core.admin.OzoneAdminSite"
