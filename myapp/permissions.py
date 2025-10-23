from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow admins to modify objects.
    """

    def has_permission(self, request, view):
        # SAFE_METHODS = GET, HEAD, OPTIONS (read-only)
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True

        # Only users with 'admin' role can create/update/delete
        return hasattr(request.user, 'is_staff') and request.user.is_staff
class RoleBasedAccessPermission(BasePermission):
    """
    Allow read access to all authenticated users.
    Allow write access (POST, PUT, DELETE) only for admins or users with role='admin'.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Always allow safe methods (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True

        # Allow if Django admin (staff or superuser)
        if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False):
            return True

        # Allow if custom user model has 'role' field and is 'admin'
        if hasattr(user, 'role') and user.role == 'admin':
            return True

        # Otherwise, deny
        return False