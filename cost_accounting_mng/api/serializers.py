from rest_framework import serializers
from django.contrib.auth.models import User
from models import Operations


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class OperationsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Operations
        fields = '__all__'
