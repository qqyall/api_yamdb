from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.permissions import (AnonimReadOnly, IsAdminOnly, IsAdminOrReadOnly,
                             IsSuperUserIsAdminIsModeratorIsAuthor,
                             IsSuperUserOrIsAdminOnly)
from reviews.models import Category, Genre, Review, Title, User

from .filters import TitleFilter
from .mixins import CreateListDestroyViewSet
from .serializers import (AuthSignupSerializer, AuthTokenSerializer,
                          CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleGetSerializer, TitleSerializer, UserSerializer)
from .constants import HTTP_METHOD_NAMES


@api_view(('POST',))
@permission_classes((AllowAny,))
def auth_signup(request):
    """Регистрация новых пользователей."""
    serializer = AuthSignupSerializer(data=request.data)
    user = User.objects.filter(
        email=request.data.get('email')
    ).first()
    if user and user.username == request.data.get('username'):
        confirmation_code = user.generate_confirmation_code()
        send_mail(
            'Your New Confirmation Code',
            f'Your new confirmation code is {confirmation_code}',
            settings.DEFAULT_FROM_EMAIL,
            (user.email,),
            fail_silently=False,
        )
        return Response({'email': user.email, 'username': user.username},
                        status=status.HTTP_200_OK)

    if user:
        return Response(
            {'detail': 'User with this email or username already exists.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if serializer.is_valid():
        user = serializer.save()
        confirmation_code = user.generate_confirmation_code()
        send_mail(
            'Your Confirmation Code',
            f'Your confirmation code is {confirmation_code}',
            settings.DEFAULT_FROM_EMAIL,
            (user.email,),
            fail_silently=False,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(('POST',))
@permission_classes((AllowAny,))
def auth_token(request):
    serializer = AuthTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = request.data.get('username')
    confirmation_code = request.data.get('confirmation_code')
    if not username or not confirmation_code:
        return Response(
            {'error': 'Both username and confirmation code are required.'},
            status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(username=username).first()
    if not user:
        return Response({'error': 'Invalid username'},
                        status=status.HTTP_404_NOT_FOUND)

    if user.check_confirmation_code(confirmation_code):
        refresh = RefreshToken.for_user(user)
        return Response(
            {'refresh': str(refresh), 'access': str(refresh.access_token)},
            status=status.HTTP_200_OK
        )
    return Response({'error': 'Invalid confirmation code'},
                    status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    permission_classes = (IsAdminOnly,)
    http_method_names = HTTP_METHOD_NAMES

    @action(
        methods=('GET', 'PATCH'),
        detail=False,
        url_path='me',
        url_name='me',
        permission_classes=(permissions.IsAuthenticated, IsAdminOrReadOnly),
    )
    def me(self, request):
        serializer = UserSerializer(request.user)
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data, partial=True,
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    permission_classes = (AnonimReadOnly | IsSuperUserOrIsAdminOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = HTTP_METHOD_NAMES
    ordering_fields = ('name', 'rating', 'year', 'genre', 'category')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleGetSerializer
        return TitleSerializer


class GenresViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoriesViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsSuperUserIsAdminIsModeratorIsAuthor)
    http_method_names = HTTP_METHOD_NAMES

    def get_title(self):
        """Возвращает объект текущего произведения."""
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, pk=title_id)

    def get_queryset(self):
        """Возвращает queryset c отзывами для текущего произведения."""
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        """Создает отзыв для текущего произведения,
        где автором является текущий пользователь."""
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsSuperUserIsAdminIsModeratorIsAuthor)
    http_method_names = HTTP_METHOD_NAMES

    def get_review(self):
        """Возвращает объект текущего отзыва."""
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, pk=review_id)

    def get_queryset(self):
        """Возвращает queryset c комментариями для текущего отзыва."""
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        """Создает комментарий для текущего отзыва,
        где автором является текущий пользователь."""
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )
