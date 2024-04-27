from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

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
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            confirmation_code = user.generate_confirmation_code()
            send_mail(
                'Your Confirmation Code',
                f'Your confirmation code is {confirmation_code}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthToken(viewsets.ModelViewSet):
    queryset = MyUser.objects.all()
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')
        try:
            user = MyUser.objects.get(username=username)
            if user.check_confirmation_code(confirmation_code):
                refresh = RefreshToken.for_user(user)
                return Response(
                    {'refresh': str(refresh),
                     'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
        except MyUser.DoesNotExist:
            pass
        return Response({'error': 'Invalid username or confirmation code'},
                        status=status.HTTP_400_BAD_REQUEST)