from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Operations, Balance


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.CharField()

    # class Meta:
    #     model = User
    #     fields = ("id", "username", "email")

class UserBalanceSerializer(serializers.ModelSerializer):

    user = serializers.StringRelatedField(source="user.username", read_only=True)
    # user = UserSerializer()
    # user = serializers.CharField()

    class Meta:
        model = Balance
        # fields = "__all__"
        fields = ("id", "user")


class BalanceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user = UserSerializer()
    balance = serializers.FloatField()


class BalanceModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = "__all__"


class UserProfileSerializer(serializers.ModelSerializer):

    # user = serializers.StringRelatedField(read_only=True)
    operations_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    # balance = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    balance = UserBalanceSerializer(many=False, read_only=True)
    # balance = serializers.PrimaryKeyRelatedField(source="balance.balance", many=False, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'operations_set', 'balance']


class OperationsSerializer(serializers.ModelSerializer):

    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Operations
        fields = '__all__'

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)


# class BalanceSerializer(serializers.ModelSerializer):
#
#     user = serializers.ReadOnlyField(source='user.username')
#
#     class Meta:
#         model = Balance
#         fields = "__all__"
