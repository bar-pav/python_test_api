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
from .models import Operations, Account, Category, User

from .utils import filter_queryset


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


class OperationView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, operation_id=None):
        if operation_id:
            operation = Operations.objects.filter(id=operation_id).first()
            if operation in request.user.operations.all():
                return Response(OperationSerializer(operation).data)
            else:
                return Response(f"You don't have operation {operation_id}.")

        queryset = request.user.operations.all()

        order_by = request.query_params.get('order_by')
        if order_by:
            queryset = queryset.order_by(order_by)

        filter_by = request.query_params.get('filter_by')
        if filter_by:
            queryset = filter_queryset(queryset, filter_by)
        else:
            last = request.query_params.get('last')
            if last and last.isdigit():
                last = int(last)
                queryset = queryset.reverse()[:last][::-1]
        serializer = OperationSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        category = self.validate_category()
        if category:
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
        return Response(f"You don't have category \'{request.data.get('category')}\'")

    def put(self, request, operation_id):
        operation = Operations.objects.filter(id=operation_id, user=request.user.id).first()
        if operation:
            serializer = OperationSerializer(operation, data=request.data, partial=True)
            if serializer.is_valid():
                new_amount = Decimal(request.data.get("amount"))
                if new_amount:
                    old_amount = operation.amount
                    account = operation.user.balance
                    account.balance = account.balance - old_amount + new_amount
                    operation.rest_balance = operation.rest_balance - (old_amount - new_amount)
                    operation.amount = new_amount
                    account.save()
                category = self.validate_category()
                if category:
                    operation.category = category
                serializer.save()
            return Response(serializer.data)
        return Response(f"You don't have operation {operation_id}.")

    def delete(self, request, operation_id):
        operation = Operations.objects.filter(id=operation_id, user=request.user.id).first()
        if operation:
            serializer = OperationSerializer(operation)
            account = operation.user.balance
            account.balance -= operation.amount
            operation.delete()
            account.save()
            return Response({"Deleted": serializer.data})
        return Response(f"You don't have operation {operation_id}.")

    def validate_category(self):
        category = Category.objects.filter(title=self.request.data.get('category')).first()
        if category in self.request.user.categories.all():
            return category
        return None


from rest_framework.decorators import renderer_classes, api_view
from rest_framework.renderers import JSONRenderer


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def serializers_test(request):
    serializer = UserSerializer(User.objects.all().first())
    return Response(serializer.data)