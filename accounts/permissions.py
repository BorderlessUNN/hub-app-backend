from rest_framework.permissions import BasePermission
from helpers.exceptions import CustomValidationException


class IsAdminUser(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        if bool(request.user and request.user.is_authenticated and request.user.is_superuser):
            return True
        else:
            raise CustomValidationException(
                msg="You do not have permission to access this resource",
                code=401
            )

class IsAuthenticatedAndAdminIfAssigned(BasePermission):
    """
    - Always requires authentication.
    - If request.data['is_admin_assigned'] is True, also requires admin.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        is_admin_assigned = bool(getattr(request, "data", {}).get("is_admin_assigned", False))
        if is_admin_assigned:
            return bool(request.user.is_staff or request.user.is_superuser)

        return True

class AllowAnyButAdminIfAssigned(BasePermission):
    """
    - If request.data['is_admin_assigned'] is True, requires admin (and therefore authenticated).
    - Otherwise allows anyone.
    """
    def has_permission(self, request, view):
        is_admin_assigned = bool(getattr(request, "data", {}).get("is_admin_assigned", False))
        if not is_admin_assigned:
            return True

        # admin-assigned path
        return bool(request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))