from rest_framework import (viewsets, permissions, mixins,
                            pagination, filters)
from django_filters.rest_framework import DjangoFilterBackend

from django.shortcuts import get_object_or_404

from posts.models import Post, Comment, Group, User
from .serializers import (PostSerializer, CommentSerializer,
                          FollowSerializer, GroupSerializer)
from .permission import IsPostAuthorOrReadOnly


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related('author')
    serializer_class = PostSerializer
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsPostAuthorOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsPostAuthorOrReadOnly)

    def get_queryset(self):
        return Comment.objects.select_related('author').filter(
            post_id=self.kwargs['post_pk']
        )

    def perform_create(self, serializer):
        post = get_object_or_404(
            Post,
            id=self.kwargs['post_pk']
        )

        serializer.save(
            author=self.request.user,
            post=post
        )


class FollowViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):

    serializer_class = FollowSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('user', 'following')
    search_fields = ('user__username', 'following__username')
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user.username)
        return user.followers.all()

    def perform_create(self, serializer):

        following_user = get_object_or_404(
            User, username=self.request.data.get('following'))

        serializer.save(
            user=self.request.user,
            following=following_user
        )
