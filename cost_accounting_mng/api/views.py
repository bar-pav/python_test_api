from decimal import Decimal

from django.shortcuts import render
from rest_framework.generics import (ListCreateAPIView, RetrieveUpdateDestroyAPIView,)
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny
from django.contrib.auth.models import User
from .serializers import UserProfileSerializer, OperationsSerializer
from rest_framework.response import Response

from .models import Operations, Balance

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

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        res = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        if res:
            return Response(serializer.data, headers=headers)
        else:
            return Response({"message": "Insuffitient funds for operation."})

    def perform_create(self, serializer):
        balance = Balance.objects.filter(user=self.request.user).first()
        if not balance:
            balance = Balance.objects.create(user=self.request.user, balance=Decimal(self.request.data['amount']))
        else:
            if Decimal(self.request.data['amount']) < 0 and balance.balance < abs(Decimal(self.request.data['amount'])):
                return 
            balance.balance += Decimal(self.request.data['amount'])
            balance.save()
        serializer.save(user=self.request.user,
                        amount=self.request.data['amount'],
                        category=self.request.data['category'],
                        organization=self.request.data['organization'])
        return 1

