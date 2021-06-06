from django.urls import path
from . import views

urlpatterns = [
    #TODO add path to users endpoint
    path('users/', views.UserListView.as_view()),
    path('users/<int:pk>/', views.UserDetailView.as_view()),
    path('posts/create/', views.PostCreateView.as_view()),
    path('posts/', views.PostListView.as_view()),
    path('posts/<int:pk>/', views.PostDetailView.as_view()),
    path('posts/<int:pk>/update/', views.PostUpdateView.as_view()),
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view()),
    path('comments/', views.CommentListCreateView.as_view()),
    path('comments/<int:pk>/', views.CommentDetailView.as_view()),
    path('categories/', views.CategoryView.as_view()),
]
