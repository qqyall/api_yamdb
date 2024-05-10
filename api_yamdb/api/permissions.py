from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """Allows access only to the owner of the object."""

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj == request.users


class IsAdminOnly(BasePermission):
    """Allows access only to admin users and superusers."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser)


class AnonimReadOnly(BasePermission):
    """Разрешает анонимному пользователю только безопасные запросы."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsSuperUserOrIsAdminOnly(BasePermission):
    """
    Предоставляет права на осуществление запросов
    только суперпользователю Джанго, админу Джанго или
    аутентифицированному пользователю с ролью admin.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.is_super_user
                 or request.user.is_admin)
        )


class IsSuperUserIsAdminIsModeratorIsAuthor(BasePermission):
    """
    Разрешает анонимному пользователю только безопасные запросы.
    Доступ к запросам PATCH и DELETE предоставляется только
    админу, аутентифицированным пользователям
    с ролью admin или moderator, а также автору объекта.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and (request.user.role == 'admin'
                 or request.user.role == 'moderator'
                 or request.user == obj.author)
        )
