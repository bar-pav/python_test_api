from django.shortcuts import render

from rest_framework.generics import (ListCreateAPIView, RetrieveUpdateDestroyAPIView,)
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .serializers import userProfileSerializer

# Create your views here.


class UserProfileListCreateView(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = userProfileSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class UserProfileDetailView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = userProfileSerializer

