from rest_framework.exceptions import APIException


class CustomValidationException(APIException):
    default_msg = "You do not have the required permissions to complete the action you have requested for."

    def __init__(self, msg=None, code=None):
        if msg is not None:
            self.msg = msg
        else:
            self.msg = self.default_msg
        self.detail = {'msg': self.msg}

        if code is None:
            self.status_code = 400
        else:
            self.status_code = code