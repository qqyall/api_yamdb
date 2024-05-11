from rest_framework import viewsets

from api.serializers import (AuthorOrReadOnly, CommentSerializer, ReadOnly,
                             ReviewSerializer)
from reviews.models import Comment, Review


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = None

    def get_permissions(self):
        if self.action == 'retrieve':
            return (ReadOnly(),)
        return super().get_permissions()

    def get_comment_id_kwarg(self):
        return {'comment_id': self.kwargs['comment_id']}

    def get_queryset(self):
        return Review.objects.filter(**self.get_comment_id_kwarg())

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user, **self.get_comment_id_kwarg())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = None

    def get_permissions(self):
        if self.action == 'retrieve':
            return (ReadOnly(),)
        return super().get_permissions()

    def get_post_id_kwarg(self):
        return {'post_id': self.kwargs['post_id']}

    def get_queryset(self):
        return Comment.objects.filter(**self.get_post_id_kwarg())

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user, **self.get_post_id_kwarg())
