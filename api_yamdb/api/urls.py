from django.urls import include, path

from rest_framework import routers

from .views import (
    UserViewSet, TitlesViewSet, GenresViewSet, CategoriesViewSet,
    ReviewViewSet, CommentViewSet, AuthSignup, AuthToken
)

from api.views import UserMeView

router = routers.DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register('titles', TitlesViewSet, basename='titles')
router.register('categories', CategoriesViewSet, basename='categories')
router.register('genres', GenresViewSet, basename='genres')
router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comment'
)

urlpatterns = [
    path('auth/signup/', AuthSignup.as_view({'post': 'create'}), name='signup'),
    path('users/me/', UserMeView.as_view(), name='user-me'),
    path('auth/token/', AuthToken.as_view({'post': 'create'}), name='token'),
    path('', include(router.urls)),
]
