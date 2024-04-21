from django.urls import include, path, re_path
from rest_framework.authtoken import views as auth_views
from rest_framework.routers import DefaultRouter
from . import views


urlpatterns = [
    path("register", views.UserView.as_view(), name='create_user'),
    path("user", views.UserView.as_view(), name='user'),
    path("obtain-token", auth_views.obtain_auth_token),
    path("account", views.AccountView.as_view(), name='account'),
    path('operations', views.OperationView.as_view(), name='operations'),
    path('all-operations', views.UserOperationsListCreateView.as_view(), name='all-operations'),
    path('categories', views.CategoryView.as_view(), name='categories'),
]
