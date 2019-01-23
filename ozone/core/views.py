from django.conf import settings
from django.shortcuts import render
from django.views.i18n import set_language as set_language_django

from ozone.core.models import Language

# Create your views here.
def spabundle(request):
    return render(request, 'bundle.html')


def set_language(request):
    """Override the default Django set language view to also store
    the user language in the model.
    """
    response = set_language_django(request)

    if request.user.is_authenticated:
        try:
            language = response.cookies[settings.LANGUAGE_COOKIE_NAME].value
            request.user.language = Language.objects.get(language_id=language)
            request.user.save()
        except (KeyError, Language.DoesNotExist):
            pass
    return response
