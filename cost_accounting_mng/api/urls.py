from django.urls import include, path
from rest_framework.routers import DefaultRouter


# from .views import UserProfileDetailView
from .views import UserProfileListCreateView, UserOperaionsListCreateView


urlpatterns = [
    path("all-profiles", UserProfileListCreateView.as_view(), name='all-profiles'),
    path('all-operations', UserOperaionsListCreateView.as_view(), name='all-operations'),
    # path("profile/<int:pk>", UserProfileDetailView.as_view(), name='profile'),
]
