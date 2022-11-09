from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Operations


class UserProfileSerializer(serializers.ModelSerializer):

    # user = serializers.StringRelatedField(read_only=True)
    operations_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = '__all__'


class OperationsSerializer(serializers.ModelSerializer):

    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Operations
        fields = '__all__'

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)