from decimal import Decimal

from django.shortcuts import render
from rest_framework.generics import (ListCreateAPIView, RetrieveUpdateDestroyAPIView,)
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny
from django.contrib.auth.models import User
from .serializers import UserProfileSerializer, OperationsSerializer, BalanceSerializer
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
    balance_serializer = BalanceSerializer

    def get_queryset(self):
        # return Operations.objects.filter()
        return Operations.objects.filter(user=self.request.user)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        res = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        if res:
            serializer.data["balance"] = str(self.request.user.balance)
            return Response((serializer.data), headers=headers)
        else:
            return Response({"message": "Insuffitient funds for operation.", "balance": str(self.request.user.balance)})

    # def perform_create(self, serializer):
    #     amount = Decimal(self.request.data['amount'])
    #     balance_record = Balance.objects.filter(user=self.request.user).first()
    #     if not balance_record and amount > 0:
    #         balance_record = Balance.objects.create(user=self.request.user, balance=amount)
    #     else:
    #         if amount < 0 and balance_record.balance < abs(amount):
    #             return 
    #         balance_record.balance += amount
    #         balance_record.save()
    #     serializer.save(user=self.request.user,
    #                     amount=self.request.data['amount'],
    #                     category=self.request.data['category'],
    #                     organization=self.request.data['organization'])
    #     return 1

    def perform_create(self, serializer):
        amount = Decimal(self.request.data['amount'])
        balance_record = Balance.objects.filter(user=self.request.user).first()
        if not balance_record and amount > 0:
            balance_record = self.balance_serializer.save(user=self.request.user, balance=amount)
        else:
            if amount < 0 and balance_record.balance < abs(amount):
                return 
            balance_record.balance += amount
            balance_record.save()
        return serializer.save(user=self.request.user,
                        amount=self.request.data['amount'],
                        rest_balance=balance_record.balance,
                        category=self.request.data['category'],
                        organization=self.request.data['organization'])
        # print(self.request.data['amount'])
        # return serializer.save(data=self.request.data)

