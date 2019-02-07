import traceback
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from sentry_sdk import capture_exception


User = get_user_model()


class ExceptionMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, ValidationError):
            status = 422
            if hasattr(exception, 'error_dict'):
                exception_dict = exception.message_dict
            else:
                exception_dict = {
                    NON_FIELD_ERRORS: []
                }
                for message in exception.messages:
                    exception_dict[NON_FIELD_ERRORS].append(message)
        elif hasattr(exception, "status_code"):
            status = exception.status_code
            exception_dict = exception.to_dict()
        else:
            capture_exception(exception)
            status = 500
            exception_dict = {
                NON_FIELD_ERRORS: ['Unexpected Error!']
            }

        traceback.print_exc()
        return JsonResponse(exception_dict, status=status)


class TokenAdminAuthMiddleware(object):
    """Authenticated the user automatically if the authToken cookies is set."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # See django.contrib.auth.middleware.AuthenticationMiddleware
        if not hasattr(request, '_cached_user'):
            try:
                token = Token.objects.select_related('user').get(key=request.COOKIES['authToken'])
                if token.user.is_active:
                    request._cached_user = token.user
            except (Token.DoesNotExist, KeyError):
                pass
        response = self.get_response(request)
        return response


class ImpersonateTokenAuthMiddleware(object):
    """Sets the authToken cookie after the impersonate is triggered.
    This allows the FE app to behave like the impersonated user is logged in.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if getattr(request.user, "is_impersonate", False):
            token, created = Token.objects.get_or_create(user=request.user)
            response.set_cookie("authToken", token.key)
        return response
