from django.conf import settings
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.views import serve
from django.views import defaults as default_views
from django.views.generic import RedirectView

urlpatterns = [
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management

    # Your stuff: custom urls includes go here
    path(
        "",
        RedirectView.as_view(url='/reporting', permanent=False)
    ),
    re_path(
        r"^reporting/.*",
        serve,
        kwargs={'path': 'index.html'}
    ),
    re_path(
        r"^(?!/?static/)(?!/?media/)(?P<path>.*\..*)$",
        RedirectView.as_view(url='/static/%(path)s', permanent=False)
    ),
    path(
        "api/",
        include("ozone.core.api.urls",namespace="core")
    ),
] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    # This allows browsable API authentication
    urlpatterns += [
        path('api-auth/', include('rest_framework.urls')),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
