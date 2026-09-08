from rest_framework import serializers
from django.db import connection
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone_number', 'is_logged_in', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=15)

    def validate_phone_number(self, value):
        try:
            # Check if user exists
            if User.objects.filter(phone_number=value).exists():
                raise serializers.ValidationError("User with this phone number already exists")
        except Exception as e:
            # If there's a database error, log it but proceed
            print(f"Database error in validation: {e}")
            # Don't raise the error, let the create handle it
            pass
        return value

    def create(self, validated_data):
        try:
            return User.objects.create(**validated_data)
        except Exception as e:
            # If creation fails, raise a validation error
            raise serializers.ValidationError(f"Failed to create user: {str(e)}")

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

    def validate_phone_number(self, value):
        try:
            user = User.objects.get(phone_number=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found with this phone number")
        except Exception as e:
            raise serializers.ValidationError(f"Database error: {str(e)}")

    def login_user(self):
        phone_number = self.validated_data['phone_number']
        user = User.objects.get(phone_number=phone_number)
        user.is_logged_in = True
        user.save()
        return user