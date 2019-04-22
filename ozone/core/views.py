from django.conf import settings
from django.contrib.auth.views import PasswordResetConfirmView
from django.shortcuts import render
from django.views.i18n import set_language as set_language_django

from ozone.core.email import send_mail_from_template
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


class ActivateUserPasswordResetConfirmView(PasswordResetConfirmView):

    def form_valid(self, form):
        result = super().form_valid(form)
        # First password reset
        if not self.user.activated:
            self.user.activated = True
            self.user.save()
            if self.user.created_by is not None:
                # Send email to the admin that created this user.
                send_mail_from_template(
                    "registration/account_activated_subject.txt",
                    "registration/account_activated_email.html",
                    context={
                        "account": self.user,
                        "site_name": self.request.META.get("HTTP_HOST")
                    },
                    to_email=self.user.created_by.email
                )
        return result
