from rest_framework import viewsets, permissions
from rest_framework import pagination
from rest_framework import filters
from rest_framework import exceptions

from posts.models import Post, Comment, Follow, Group, User
from .serializers import (PostSerializer, CommentSerializer,
                          FollowSerializer, GroupSerializer)


from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
import django_filters

from django.shortcuts import get_object_or_404


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related('author')
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = pagination.LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
        )

    def update(self, request, *args, **kwargs):
        user = self.request.user
        post = self.get_object()
        if user != post.author:
            return Response(
                {'Detail': 'You do not have permission to perform'
                 'this action.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        post = self.get_object()
        if user != post.author:
            return Response(
                {'Detail': 'You do not have permission to perform'
                 'this action.'},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().destroy(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

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

    def update(self, request, *args, **kwargs):
        user = self.request.user
        comment = self.get_object()
        if user != comment.author:
            return Response(
                {'Detail': 'You do not have permission to perform'
                 'this action.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = CommentSerializer(
            comment, data=request.data, partial=True)

        if serializer.is_valid():
            post = Post.objects.get(
                id=self.kwargs['post_pk']
            )
            serializer.save(
                author=self.request.user,
                post=post
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        post = self.get_object()
        if user != post.author:
            return Response(
                {'Detail': 'You do not have permission to perform'
                 'this action.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class FollowViewSet(viewsets.ModelViewSet):

    serializer_class = FollowSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('user', 'following')
    search_fields = ('user', 'following')

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user.username)
        return user.followers.all()
        # return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        following_user = get_object_or_404(
            User, username=self.request.data['following']
        )
        if following_user == self.request.user:
            raise exceptions.ValidationError("You cannot follow yourself.")
        if Follow.objects.filter(user=self.request.user,
                                 following=following_user).exists():
            raise exceptions.ValidationError(
                "You are already following this user.")
        serializer.save(user=self.request.user, following=following_user)
