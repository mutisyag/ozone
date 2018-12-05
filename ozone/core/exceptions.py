
class BaseCustomException(Exception):
    status_code = None
    error_message = None
    fields = None

    def __init__(self, error_message, field=None):
        Exception.__init__(self)
        self.error_message = error_message
        if field is None:
            self.field = []
        else:
            self.field = field

    def to_dict(self):
        return {
            'error_message': self.error_message,
            'fields': self.field
        }


class CustomValidationError(BaseCustomException):
    status_code = 422


class InvalidRequest(BaseCustomException):
    status_code = 400


class MethodNotAllowed(BaseCustomException):
    status_code = 405


class StateDoesNotExist(BaseCustomException):
    status_code = 412


class TransitionDoesNotExist(BaseCustomException):
    status_code = 412


class TransitionNotAvailable(BaseCustomException):
    status_code = 412
