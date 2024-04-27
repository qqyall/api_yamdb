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

# router.register('auth/signup/', AuthSignup, basename='signup')
# router.register('auth/token/', AuthToken, basename='token',)

urlpatterns = [
    # Map the 'create' action from the AuthSignup viewset to the 'POST' method
    path('auth/signup/', AuthSignup.as_view({'post': 'create'}), name='signup'),
    # Map the 'create' action from the AuthToken viewset to the 'POST' method
    path('auth/token/', AuthToken.as_view({'post': 'create'}), name='token'),
    # Include all routes registered with the router
    path('', include(router.urls)),
]
