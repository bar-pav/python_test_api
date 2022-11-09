from django.shortcuts import render

from rest_framework.generics import (ListCreateAPIView, RetrieveUpdateDestroyAPIView,)
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny
from django.contrib.auth.models import User
from .serializers import UserProfileSerializer, OperationsSerializer

from .models import Operations

# Create your views here.


class UserProfileListCreateView(ListCreateAPIView):
    # queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        print('User:', self.request.user.id)
        return User.objects.all()

    # def perform_create(self, serializer):
    #     user = self.request.user
    #     serializer.save(user=user)

#
# class UserProfileDetailView(RetrieveUpdateDestroyAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserProfileSerializer


class UserOperationsListCreateView(ListCreateAPIView):
    # queryset = Operations.objects.all()
    serializer_class = OperationsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # return Operations.objects.filter()
        return Operations.objects.filter(user=self.request.user)

