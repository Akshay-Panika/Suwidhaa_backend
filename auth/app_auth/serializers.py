from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone_number', 'is_logged_in', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']