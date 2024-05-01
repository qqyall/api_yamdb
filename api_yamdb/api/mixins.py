from rest_framework import filters, mixins, viewsets

from .permissions import AnonimReadOnly, IsSuperUserOrIsAdminOnly


class CreateListDestroyViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    """Вьюсет, позволяющий осуществлять GET, POST и DELETE запросы."""

    permission_classes = (AnonimReadOnly | IsSuperUserOrIsAdminOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
