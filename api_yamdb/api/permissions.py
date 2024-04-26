from rest_framework.permissions import BasePermission


class IsAdminOrReadOnly(BasePermission):
    pass


class IsAdminOnly(BasePermission):
    pass


class IsOwnerAdminModeratorOrReadOnly(BasePermission):
    pass
