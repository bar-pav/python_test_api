from decimal import Decimal
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Operations, Account, Category


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "password", "email")
        read_only_fields = ['id', 'operations']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        default_categories = Category.objects.filter(inf="D").all()
        user.categories.add(*default_categories)
        return user


class UserAccountSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(source="user.username", read_only=True)

    class Meta:
        model = Account
        fields = ("id", "user", "balance")


class AccountSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    balance = serializers.FloatField()

    def update(self, instance, validated_data):
        print(validated_data)
        instance.balance += Decimal(validated_data.get("balance"))
        instance.save()
        return instance


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title"]
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


class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operations
        fields = '__all__'
        extra_kwargs = {"user": {"read_only": True},
                        "category": {"read_only": True},
                        "rest_balance": {"read_only": True}}
