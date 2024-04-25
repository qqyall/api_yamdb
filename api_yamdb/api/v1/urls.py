from django.urls import include, path

from rest_framework import routers

from .views import (
    UserViewSet, TitlesViewSet, GenresViewSet, CategoriesViewSet,
    ReviewViewSet, CommentViewSet, AuthSignup, AuthToken
)


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
    # надо подумать над auth/signup/ и auth/token/
    path('auth/signup/', AuthSignup.as_view(), name='signup'),
    path('auth/token/', AuthToken.as_view(), name='token'),
    path('', include(router.urls)),
]
