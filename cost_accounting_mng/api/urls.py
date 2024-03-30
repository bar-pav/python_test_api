from django.urls import include, path
from rest_framework.routers import DefaultRouter


# from .views import UserProfileDetailView
from .views import UserProfileListCreateView, UserOperationsListCreateView, UserOperationsList, ListUsers, ListUserBalance



urlpatterns = [
    path("users", ListUsers.as_view(), name='users'),
    path("balances", ListUserBalance.as_view(), name='balances'),
    path("all-profiles", UserProfileListCreateView.as_view(), name='all-profiles'),
    path('all-operations', UserOperationsListCreateView.as_view(), name='all-operations'),
    path('operations', UserOperationsList.as_view(), name='all-operations'),

    # path("profile/<int:pk>", UserProfileDetailView.as_view(), name='profile'),
]
