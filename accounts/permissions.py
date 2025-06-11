from rest_framework.permissions import BasePermission
from helpers.exceptions import CustomValidationException


class IsAdminUser(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        if bool(request.user and request.user.is_authenticated):
            return True
        else:
            raise CustomValidationException(
                msg="You do not have permission to access this resource",
                code=401
            )

