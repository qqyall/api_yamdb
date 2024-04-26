from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.permissions import (
    IsAdminOnly, IsAdminOrReadOnly, IsOwnerAdminModeratorOrReadOnly
)
from reviews.models import Title, Genre, Category, MyUser
from .serializers import (
    TitleSerializer, GenreSerializer, CategorySerializer, ReviewSerializer,
    CommentSerializer, MyUserSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer
    permission_classes = (IsAdminOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)


class GenresViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsOwnerAdminModeratorOrReadOnly)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsOwnerAdminModeratorOrReadOnly)


class AuthSignup(viewsets.ModelViewSet):
    pass


class AuthToken(viewsets.ModelViewSet):
    pass
