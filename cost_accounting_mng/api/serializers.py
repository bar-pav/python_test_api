from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Operations, Account, Category


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.CharField()

    # class Meta:
    #     model = User
    #     fields = ("id", "username", "email")

class UserAccountSerializer(serializers.ModelSerializer):

    user = serializers.StringRelatedField(source="user.username", read_only=True)
    # user = UserSerializer()
    # user = serializers.CharField()

    class Meta:
        model = Account
        # fields = "__all__"
        fields = ("id", "user", "balance")


class AccountSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user = UserSerializer()
    balance = serializers.FloatField()


class AccountModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ["users"]

    def create(self, validated_data):
        existed = Category.objects.filter(title__iexact=validated_data.get("title")).first()
        if existed:
            existed.users.add(validated_data.get("user"))
            return existed
        else:
            category = Category.objects.create(title=validated_data.get("title"))
            category.users.add(validated_data.get("user"))
            return category


class UserProfileSerializer(serializers.ModelSerializer):

    # user = serializers.StringRelatedField(read_only=True)
    operations_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    # balance = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    balance = UserAccountSerializer(many=False, read_only=True)
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
#         model = Account
#         fields = "__all__"
