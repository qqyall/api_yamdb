from rest_framework.permissions import BasePermission


class IsAdminOrReadOnly(BasePermission):
    pass


class IsAdminOnly(BasePermission):
    """Allows access only to admin users."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsOwnerAdminModeratorOrReadOnly(BasePermission):
    pass
