from django.conf import settings
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.views import serve
from django.views import defaults as default_views
from django.views.generic import RedirectView
from django.conf.urls import url
from rest_framework.documentation import include_docs_urls

from ozone.core import views


urlpatterns = [
    # Cannot add this in the api.urls because of
    # https://github.com/encode/django-rest-framework/issues/4984
    # XXX Change me after upgrade to a version that has this fix.
    url(r'^api/docs/', include_docs_urls(title='ORS API', public=False)),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    path('admin/i18n/setlang/', views.set_language, name='set_language'),
    # url(', include('django.conf.urls.i18n')),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    # User management
    path(
        'admin/password_reset/',
        auth_views.PasswordResetView.as_view(),
        name='admin_password_reset',
    ),
    path(
        'admin/password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete',
    ),
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
