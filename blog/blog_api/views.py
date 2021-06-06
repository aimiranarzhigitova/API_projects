from django.db import connection
from django_filters import rest_framework as filters
from rest_framework import generics
from rest_framework import permissions
from blog_api import serializers
from django.contrib.auth.models import User

from blog_api.models import Post, Comment, Category
from blog_api.permissions import IsOwnerOrReadOnly


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = serializers.RegisterSerializer


class UserListView(generics.ListAPIView):
    """Endpoint for retrieve all user
    """
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class UserDetailView(generics.RetrieveAPIView):
    """Endpoint for retrieve single user
    """
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class PostListView(generics.ListAPIView):
    """Endpoint for retrieve all posts
    """
    queryset = Post.objects.select_related('owner', 'category')
    serializer_class = serializers.PostSerializer
    filter_backends = (filters.DjangoFilterBackend, )
    filterset_fields = ('title', 'category')

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        print(f'Queries Counted: {len(connection.queries)}')
        return response


class PostCreateView(generics.CreateAPIView):
    """Endpoint for create post:
    only authenticated user
    """
    serializer_class = serializers.PostSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PostDetailView(generics.RetrieveAPIView):
    """Endpoint for retrieve single post
    """
    queryset = Post.objects.all()
    serializer_class = serializers.PostSerializer


class PostDeleteView(generics.DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, )


class PostUpdateView(generics.UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, )


class CommentListCreateView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)


class CategoryView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer

