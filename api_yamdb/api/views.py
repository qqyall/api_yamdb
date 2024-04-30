from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import permissions
from rest_framework.views import APIView
from django.db.models import Q

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
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    permission_classes = [IsAdminOnly]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAdminOnly()]
        return super().get_permissions()


    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response({'detail': 'Method "PUT" not allowed.'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)


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
        user = MyUser.objects.filter(
            email=request.data.get('email')
        ).first()

        if user and user.username == request.data.get('username'):
            # Generate a new confirmation code and send it
            confirmation_code = user.generate_confirmation_code()
            send_mail(
                'Your New Confirmation Code',
                f'Your new confirmation code is {confirmation_code}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return Response({'email': user.email, 'username': user.username},
                            status=status.HTTP_200_OK)

        if user:
            # Block registration if username or email already used differently
            return Response(
                {"detail": "User with this email or username already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Handle new user registration
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
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthToken(viewsets.ViewSet):
    """
    Custom view for handling authentication token creation.
    """
    permission_classes = [AllowAny]  # Allow requests without authentication

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')

        if not username or not confirmation_code:
            # If either username or confirmation code is missing, return 400 Bad Request
            return Response(
                {'error': 'Both username and confirmation code are required.'},
                status=status.HTTP_400_BAD_REQUEST)

        user = MyUser.objects.filter(username=username).first()
        if not user:
            # If user does not exist, return 404 Not Found
            return Response({'error': 'Invalid username'},
                            status=status.HTTP_404_NOT_FOUND)

        if user.check_confirmation_code(confirmation_code):
            refresh = RefreshToken.for_user(user)
            return Response(
                {'refresh': str(refresh), 'access': str(refresh.access_token)},
                status=status.HTTP_200_OK
            )
        else:
            # If the confirmation code is invalid, return 400 Bad Request
            return Response({'error': 'Invalid confirmation code'},
                            status=status.HTTP_400_BAD_REQUEST)


class UserMeView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    def get(self, request):
        serializer = MyUserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = MyUserSerializer(user, data=request.data, partial=True,
                                      context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
