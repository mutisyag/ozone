import traceback
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.http import JsonResponse


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
            status = 500
            exception_dict = {
                NON_FIELD_ERRORS: ['Unexpected Error!']
            }

        traceback.print_exc()
        return JsonResponse(exception_dict, status=status)
