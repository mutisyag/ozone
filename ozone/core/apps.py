from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class CoreConfig(AppConfig):
    name = 'ozone.core'
    verbose_name = "Ozone Reporting Core"

    def ready(self):
        """Overriding ready to make sure signals are connected"""
        from . import signals
        super().ready()


class OzoneAdminConfig(AdminConfig):
    default_site = "ozone.core.admin.OzoneAdminSite"
