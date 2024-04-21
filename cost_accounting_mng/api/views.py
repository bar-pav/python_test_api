from decimal import Decimal

from django.shortcuts import render
from rest_framework.generics import (ListCreateAPIView, RetrieveUpdateDestroyAPIView,GenericAPIView)
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from .serializers import (
                          OperationSerializer,
                          AccountSerializer,
                          UserSerializer,
                          CategorySerializer,
                          )
from rest_framework.response import Response
from .models import Operations, Account, Category


class UserView(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        if request.user.is_authenticated:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        return Response('Not authenticated. Set Token in headers first.')

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            Account.objects.create(user=user)
            token = Token.objects.create(user=user)
            return Response({"Token": token.key})
        else:
            return Response(serializer.errors)


class AccountView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = AccountSerializer(request.user.balance)
        return Response(serializer.data)


class OperationView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, operation_id=None):
        if operation_id:
            if operation_id in request.user.operation:
                return Response(str(Operations.objects.get(id=operation_id)))
            else:
                return Response(f"You have no operation {operation_id}.")
        count = request.query_params.get('count')
        if count and count.isdigit():
            count = int(count)
        else:
            count = 10
        serializer = OperationSerializer(request.user.operations.all().reverse()[:count], many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        category = Category.objects.filter(title=request.data.get('category')).first()
        if category and category in user.categories.all():
            operation_serializer = OperationSerializer(data=request.data)
            if operation_serializer.is_valid():
                balance_serializer = AccountSerializer(user.balance,
                                                       data={"balance": operation_serializer.validated_data.get("amount")},
                                                       partial=True)
                if balance_serializer.is_valid():
                    balance_serializer.save()
                else:
                    return Response(balance_serializer.errors)
                operation_serializer.save(user=user, category=category, rest_balance=balance_serializer.data.get("balance"))
                return Response(operation_serializer.data)
            else:
                return Response(operation_serializer.errors)
        return Response(f"You have no category \'{request.data.get('category')}\'")


class CategoryList(APIView):
    def get(self, request):
        categories_serial = CategorySerializer(Category.objects.all(), many=True)
        return Response(categories_serial.data)


class CategoryView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = CategorySerializer(user.categories.all(), many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
        return Response(serializer.data)


# class AccountListView(APIView):
#     def get(self, request):
#         balances = Account.objects.all()
#         balances_serial = AccountModelSerializer(balances, many=True)
#         return Response(balances_serial.data)


# class UserProfileListCreateView(ListCreateAPIView):
#     # queryset = User.objects.all()
#     serializer_class = UserProfileSerializer
#     permission_classes = (AllowAny,)
#
#     def get_queryset(self):
#         print('User:', self.request.user.id)
#         return User.objects.all()
#
#     def perform_create(self, serializer):
#         user = serializer.save()
#         balance = Account(user=user, balance=0)
#         balance.save()


class UserOperationsListCreateView(APIView):
    # queryset = Operations.objects.all()
    serializer_class = OperationSerializer
    # permission_classes = (IsAuthenticated,)
    balance_serializer = OperationSerializer

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
        serializer = OperationSerializer(operations, many=True)
        return Response(serializer.data)

    def post(self, request):
        amount = Decimal(self.request.data['amount'])
        balance_record = Account.objects.filter(user=self.request.user).first()
        if not balance_record and amount > 0:
            serializer = OperationSerializer(user=self.request.user, amount=self.request.data['amount'],
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
            serializer = OperationSerializer(user=self.request.user,
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
