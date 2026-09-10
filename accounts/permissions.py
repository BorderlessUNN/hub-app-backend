from rest_framework.permissions import BasePermission
from helpers.exceptions import CustomValidationException


class IsAdminUser(BasePermission):
    """
    Allows access only to admin users (either tier — Super or Staff Admin).
    """

    def has_permission(self, request, view):
        if bool(request.user and request.user.is_authenticated and request.user.is_superuser):
            return True
        else:
            raise CustomValidationException(
                msg="You do not have permission to access this resource",
                code=401
            )

class IsSuperAdminUser(BasePermission):
    """
    Allows access only to Super Admin users (Staff Admins are rejected).
    """

    def has_permission(self, request, view):
        if bool(request.user and request.user.is_authenticated and request.user.is_super_admin):
            return True
        else:
            raise CustomValidationException(
                msg="Only a Super Admin can perform this action",
                code=401
            )

class IsAuthenticatedAndAdminIfAssigned(BasePermission):
    """
    - Always requires authentication.
    - If request.data['is_admin_assigned'] is True, requires a Super Admin
      specifically — manually assigning a free subscription is a Super
      Admin-only capability. Staff Admins can still hit this endpoint for
      the Paystack-initiated (is_admin_assigned=False) path.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        is_admin_assigned = bool(getattr(request, "data", {}).get("is_admin_assigned", False))
        if is_admin_assigned:
            if bool(request.user.is_super_admin):
                return True
            raise CustomValidationException(
                msg="Only a Super Admin can manually assign a subscription",
                code=401
            )

        return True

class AllowAnyButAdminIfAssigned(BasePermission):
    """
    - If request.data['is_admin_assigned'] is True, requires a Super Admin
      specifically (manually assigning a free subscription is Super
      Admin-only).
    - Otherwise allows anyone (self-service non-member booking).
    """
    def has_permission(self, request, view):
        is_admin_assigned = bool(getattr(request, "data", {}).get("is_admin_assigned", False))
        if not is_admin_assigned:
            return True

        if bool(request.user and request.user.is_authenticated and request.user.is_super_admin):
            return True
        raise CustomValidationException(
            msg="Only a Super Admin can manually assign a subscription",
            code=401
        )
