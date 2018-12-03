import traceback
from django.http import JsonResponse


class ExceptionMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if hasattr(exception, "status_code"):
            status = exception.status_code
            exception_dict = exception.to_dict()
        else:
            status = 500
            exception_dict = {'error_message': 'Unexpected Error!'}

        traceback.print_exc()
        return JsonResponse(exception_dict, status=status)
