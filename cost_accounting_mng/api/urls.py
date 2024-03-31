from django.urls import include, path
from rest_framework.routers import DefaultRouter


# from .views import UserProfileDetailView
from .views import (UserProfileListCreateView,
                    UserOperationsListCreateView,
                    UserOperationsList,
                    UserListView,
                    UserDetailView,
                    AccountListView,
                    AccountView,
                    CreateCategory,
                    CategoryList,
                    )


urlpatterns = [
    path("users", UserListView.as_view(), name='users'),
    path("user/<user_id>", UserDetailView.as_view(), name='user'),
    path("accounts", AccountListView.as_view(), name='accounts'),
    path("account/<user_id>", AccountView.as_view(), name='account'),
    path("all-profiles", UserProfileListCreateView.as_view(), name='all-profiles'),
    path('all-operations', UserOperationsListCreateView.as_view(), name='all-operations'),
    path('operations', UserOperationsList.as_view(), name='all-operations'),

    path('categories', CategoryList.as_view(), name='categories'),
    path('create-category', CreateCategory.as_view(), name='create-category'),


    # path("profile/<int:pk>", UserProfileDetailView.as_view(), name='profile'),
]
