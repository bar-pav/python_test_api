from decimal import Decimal

from django.shortcuts import render
from rest_framework.generics import (ListCreateAPIView, RetrieveUpdateDestroyAPIView,)
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny
from django.contrib.auth.models import User
from .serializers import (UserProfileSerializer,
                          OperationsSerializer,
                          BalanceSerializer,
                          BalanceModelSerializer,
                          UserSerializer,
                          )
from rest_framework.response import Response

from .models import Operations, Balance

# Create your views here.


class UserListView(APIView):
    def get(self, request):
        users = User.objects.all()
        users_serial = UserSerializer(users, many=True)
        return Response(users_serial.data)


class UserDetailView(APIView):
    def get(self, request, user_id=None):
        print("------------------->", user_id)
        if user_id:
            user = User.objects.filter(id=user_id).first()
            if user:
                user_serial = UserSerializer(user)
                return Response(user_serial.data)
            return Response(f"No such user with id={user_id}")


class BalanceListView(APIView):
    def get(self, request):
        balances = Balance.objects.all()
        balances_serial = BalanceModelSerializer(balances, many=True)
        return Response(balances_serial.data)


class BalanceView(APIView):
    def get(self, request, user_id=None):
        print("------------------->", user_id)
        if user_id:
            # balance = Balance.objects.filter(user__id=user_id).first()
            user = User.objects.filter(id=user_id).first()
            print(user.balance)
            if user:
                balance = user.balance
            else:
                balance = None
            print(balance)
            if balance:
                balance_serial = BalanceSerializer(balance)
                return Response(balance_serial.data)
            return Response(f"No such user with id={user_id}")


class UserProfileListCreateView(ListCreateAPIView):
    # queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        print('User:', self.request.user.id)
        return User.objects.all()

    def perform_create(self, serializer):
        user = serializer.save()
        balance = Balance(user=user, balance=0)
        balance.save()

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
            if amount < 0 and balance_record.balance < abs(amount):
                return Response({"message": "Insuffitient funds for operation.", "balance": str(self.request.user.balance)},
                status=status.HTTP_400_BAD_REQUEST)
            balance_record.balance += amount
            balance_record.save()
            operation.save(user=self.request.user,
                        rest_balance=balance_record.balance)
            return Response(operation.data, status=status.HTTP_201_CREATED)
        return Response(operation.errors, status=status.HTTP_400_BAD_REQUEST)
