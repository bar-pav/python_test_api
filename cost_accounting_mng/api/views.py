from decimal import Decimal

from django.shortcuts import render
from rest_framework.generics import (ListCreateAPIView, RetrieveUpdateDestroyAPIView,)
from rest_framework.views import APIView
from rest_framework import status
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


class UserOperationsListCreateView(APIView):
    # queryset = Operations.objects.all()
    serializer_class = OperationsSerializer
    permission_classes = (IsAuthenticated,)
    balance_serializer = BalanceSerializer

    def get_queryset(self):
        return Operations.objects.filter(user=self.request.user)

    def get(self, request):
        operations = OperationsSerializer(Operations.objects.all(), many=True)
        return Response(operations.data)

    def post(self, request):
        amount = Decimal(request.data['amount'])
        operation = OperationsSerializer(data=request.data)
        if operation.is_valid():
            balance_record = Balance.objects.filter(user=self.request.user).first()
            if not balance_record and amount > 0:
                balance_record = self.balance_serializer.save(user=self.request.user, balance=amount)
            else:
                if amount < 0 and balance_record.balance < abs(amount):
                    return Response({"message": "Insuffitient funds for operation.", "balance": str(self.request.user.balance)})
                balance_record.balance += amount
                balance_record.save()
                operation.save(user=self.request.user,
                            rest_balance=balance_record.balance)
                return Response(operation.data)
        return Response(operation.errors, status=status.HTTP_400_BAD_REQUEST)
