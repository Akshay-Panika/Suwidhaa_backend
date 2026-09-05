from rest_framework import serializers
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
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("User with this phone number already exists")
        return value

    def create(self, validated_data):
        return User.objects.create(**validated_data)

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

    def validate_phone_number(self, value):
        try:
            user = User.objects.get(phone_number=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found with this phone number")
        return value

    def login_user(self):
        phone_number = self.validated_data['phone_number']
        user = User.objects.get(phone_number=phone_number)
        user.is_logged_in = True
        user.save()
        return user