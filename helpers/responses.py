from django.conf import settings
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import serializers


class CustomResponse(Response):
    """
    This code defines a custom response class "CustomResponse" that extends the Django REST Framework's built-in "Response" class. The custom response class is designed to return a JSON response with a status code, message, and data payload.

    The constructor of the class takes in four parameters:
    - valid: a boolean indicating whether the response is valid or not.
    - msg: a string message that describes the response.
    - status: an integer representing the HTTP status code of the response. The default value is 200.
    - data: a dictionary or JSON serializable object that contains additional data to include in the response. The default value is None.

    If the "valid" parameter is False and the "status" parameter is less than or equal to 200, the "status" parameter will be set to 400 to indicate a bad request.

    The constructor then creates a dictionary "content" with "status" and "msg" keys, and sets their respective values to the "status" and "msg" parameters. If the "data" parameter is not None, it is added to the "content" dictionary with the key "data".

    Finally, the constructor calls the parent class's constructor with the "content" dictionary and the updated "status" parameter to create the response object.
    """

    def __init__(self, valid, msg=None, status=200, data=None):
        content = {
            "status": valid,
            "msg": msg,
        }
        if valid is False and status <= 201:
            status = 400
        if data:
            content["data"] = data
        super().__init__(content, status=status)


def custom_post_schema(request_serializer, response_serializer, status_code=200):
    """
    Returns an @extend_schema decorator for POST endpoints with CustomResponse format.

    Example response format:
    {
        "status": true,
        "msg": "message",
        "data": { ...response fields... }
    }
    """

    # Dynamically create a new serializer class with a unique name
    class_name = f'Wrapped{response_serializer.__name__}'
    print(class_name)

    WrappedResponseSerializer = type(
        class_name,
        (serializers.Serializer,),
        {
            'status': serializers.BooleanField(),
            'msg': serializers.CharField(),
            'data': response_serializer(required=False),
        }
    )

    return extend_schema(
        request=request_serializer,
        responses={status_code: OpenApiResponse(response=WrappedResponseSerializer)}
    )

