from decimal import Decimal

from django.shortcuts import render
from rest_framework.generics import (ListCreateAPIView, RetrieveUpdateDestroyAPIView,GenericAPIView)
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny
from django.contrib.auth.models import User
from .serializers import (UserProfileSerializer,
                          OperationsSerializer,
                          AccountSerializer,
                          UserAccountSerializer,
                          AccountModelSerializer,
                          UserSerializer,
                          CategorySerializer,
                          )
from rest_framework.response import Response

from .models import Operations, Account, Category

# Create your views here.


class CategoryList(APIView):
    def get(self, request):
        categories_serial = CategorySerializer(Category.objects.all(), many=True)
        return Response(categories_serial.data)


class CreateCategory(APIView):
    def post(self, request):
        category_serial = CategorySerializer(data=request.data)
        if category_serial.is_valid():
            category_serial.save(user=3)
        return Response(category_serial.data)


class ListUsers(APIView):
    def get(self, request, format=None):
        users = User.objects.all()
        users_serial = UserSerializer(instance=users, many=True)
        return Response(users_serial.data)

    def get_object(self): pass


class ListUserAccount(APIView):
    def get(self, request):
        user_balance = Account.objects.all()
        user_balance_serial = UserAccountSerializer(instance=user_balance, many=True)
        return Response(user_balance_serial.data)

    def post(self, request):
        balance = UserAccountSerializer(data=request.data)
        balance.is_valid()
        print(balance.data)
        # b = Account.objects.filter(user=request.data['user']).first()
        # balance.update(b, {'user': User.objects.get(id=request.data['user']), 'balance': request.data['balance']})

        # if balance.is_valid():
        #     b = Account.objects.filter(user=request.data['user']).first()
        #     balance.update(b, balance.data)
        # else:
        #     print(balance.errors)
        return Response(balance.data)


class UserListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print(request.user)
        print(request.auth)
        print(request.headers)
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


class AccountListView(APIView):
    def get(self, request):
        balances = Account.objects.all()
        balances_serial = AccountModelSerializer(balances, many=True)
        return Response(balances_serial.data)


class AccountView(APIView):
    def get(self, request, user_id=None):
        print("------------------->", user_id)
        if user_id:
            # balance = Account.objects.filter(user__id=user_id).first()
            user = User.objects.filter(id=user_id).first()
            print(user.balance)
            if user:
                balance = user.balance
            else:
                balance = None
            print(balance)
            if balance:
                balance_serial = AccountSerializer(balance)
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
        balance = Account(user=user, balance=0)
        balance.save()

#
# class UserProfileDetailView(RetrieveUpdateDestroyAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserProfileSerializer


class UserOperationsListCreateView(APIView):
    # queryset = Operations.objects.all()
    serializer_class = OperationsSerializer
    # permission_classes = (IsAuthenticated,)
    balance_serializer = UserAccountSerializer

    def get_queryset(self):
        return Operations.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        res = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        if res:
            serializer.data["balance"] = str(self.request.user.balance)
            return Response(serializer.data, headers=headers)
        else:
            return Response({"message": "Insuffitient funds for operation.", "balance": str(self.request.user.balance)})

    # def perform_create(self, serializer):
    #     amount = Decimal(self.request.data['amount'])
    #     balance_record = Account.objects.filter(user=self.request.user).first()
    #     if not balance_record and amount > 0:
    #         balance_record = Account.objects.create(user=self.request.user, balance=amount)
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
        balance_record = Account.objects.filter(user=self.request.user).first()
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


class UserOperationsList(APIView):
    # serializer_class = OperationsSerializer
    # permission_classes = (IsAuthenticated,)
    # balance_serializer = BalanceSerializer

    def get(self, request):
        operations = Operations.objects.all()
        serializer = OperationsSerializer(operations, many=True)
        return Response(serializer.data)

    def post(self, request):
        amount = Decimal(self.request.data['amount'])
        balance_record = Account.objects.filter(user=self.request.user).first()
        if not balance_record and amount > 0:
            serializer = OperationsSerializer(user=self.request.user, amount=self.request.data['amount'],
                                                  rest_balance=balance_record.balance,
                                                  category=self.request.data['category'],
                                                  organization=self.request.data['organization'])
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            if amount < 0 and balance_record.balance < abs(amount):
                return Response({"message": "Insuffitient funds for operation.",
                                 "balance": str(self.request.user.balance)})
            balance_record.balance += amount
            balance_record.save()
            serializer = OperationsSerializer(user=self.request.user,
                                                  amount=self.request.data['amount'],
                                                  rest_balance=balance_record.balance,
                                                  category=self.request.data['category'],
                                                  organization=self.request.data['organization'])
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def get_queryset(self):
    #     return Operations.objects.filter(user=self.request.user)
    #
    # def create(self, request):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     res = self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     if res:
    #         serializer.data["balance"] = str(self.request.user.balance)
    #         return Response(serializer.data, headers=headers)
    #     else:
    #         return Response({"message": "Insuffitient funds for operation.", "balance": str(self.request.user.balance)})
    #
    # # def perform_create(self, serializer):
    # #     amount = Decimal(self.request.data['amount'])
    # #     balance_record = Account.objects.filter(user=self.request.user).first()
    # #     if not balance_record and amount > 0:
    # #         balance_record = Account.objects.create(user=self.request.user, balance=amount)
    # #     else:
    # #         if amount < 0 and balance_record.balance < abs(amount):
    # #             return
    # #         balance_record.balance += amount
    # #         balance_record.save()
    # #     serializer.save(user=self.request.user,
    # #                     amount=self.request.data['amount'],
    # #                     category=self.request.data['category'],
    # #                     organization=self.request.data['organization'])
    # #     return 1
    #
    # def perform_create(self, serializer):
    #     amount = Decimal(self.request.data['amount'])
    #     balance_record = Account.objects.filter(user=self.request.user).first()
    #     if not balance_record and amount > 0:
    #         balance_record = self.balance_serializer.save(user=self.request.user, balance=amount)
    #     else:
    #         if amount < 0 and balance_record.balance < abs(amount):
    #             return
    #         balance_record.balance += amount
    #         balance_record.save()
    #     return serializer.save(user=self.request.user,
    #                            amount=self.request.data['amount'],
    #                            rest_balance=balance_record.balance,
    #                            category=self.request.data['category'],
    #                            organization=self.request.data['organization'])
