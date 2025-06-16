from rest_framework.authentication import BaseAuthentication
from django.conf import settings
from helpers.exceptions import CustomValidationException

class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get('X-API-KEY')
        expected_key = getattr(settings, 'API_KEY', None)

        if not expected_key:
            raise CustomValidationException(
                msg='A valid API key has not been configured on this server!'
            )

        if api_key != expected_key:
            raise CustomValidationException(msg='Invalid API key.')

        return None # Returning None will allow other authentication classes to run
