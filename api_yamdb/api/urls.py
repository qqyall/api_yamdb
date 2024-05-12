from django.urls import include, path
from rest_framework import routers

from api.views import auth_signup, auth_token

from .views import (CategoriesViewSet, CommentViewSet, GenresViewSet,
                    ReviewViewSet, TitlesViewSet, UserViewSet)

v1_router = routers.DefaultRouter()
v1_router.register('v1/users', UserViewSet, basename='users')
v1_router.register('v1/titles', TitlesViewSet, basename='titles')
v1_router.register('v1/categories', CategoriesViewSet, basename='categories')
v1_router.register('v1/genres', GenresViewSet, basename='genres')
v1_router.register(
    r'v1/titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
v1_router.register(
    r'v1/titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comment'
)

urlpatterns = [
    path('v1/auth/signup/', auth_signup, name='signup'),
    path('v1/auth/token/', auth_token, name='token'),
    path('', include(v1_router.urls)),
]
