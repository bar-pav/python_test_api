from django.urls import include, path
from rest_framework.routers import DefaultRouter


# from .views import UserProfileDetailView
from .views import (UserProfileListCreateView,
                    UserOperationsListCreateView,
                    UserOperationsList,
                    UserListView,
                    UserDetailView,
                    BalanceListView,
                    BalanceView)


urlpatterns = [
    path("users", UserListView.as_view(), name='users'),
    path("user/<user_id>", UserDetailView.as_view(), name='user'),
    path("balances", BalanceListView.as_view(), name='balances'),
    path("balance/<user_id>", BalanceView.as_view(), name='balance'),
    path("all-profiles", UserProfileListCreateView.as_view(), name='all-profiles'),
    path('all-operations', UserOperationsListCreateView.as_view(), name='all-operations'),
    path('operations', UserOperationsList.as_view(), name='all-operations'),

    # path("profile/<int:pk>", UserProfileDetailView.as_view(), name='profile'),
]
