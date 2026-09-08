from rest_framework import serializers
from django.db import connection
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone_number', 'is_logged_in', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=100,
        error_messages={
            'required': 'Name is required',
            'blank': 'Name cannot be empty',
            'max_length': 'Name cannot exceed 100 characters'
        }
    )
    phone_number = serializers.CharField(
        max_length=15,
        error_messages={
            'required': 'Phone number is required',
            'blank': 'Phone number cannot be empty',
            'max_length': 'Phone number cannot exceed 15 characters'
        }
    )

    def validate_phone_number(self, value):
        # Clean phone number (remove spaces, special characters)
        value = ''.join(filter(str.isdigit, value))
        
        if len(value) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits")
        
        # Check if user exists
        try:
            if User.objects.filter(phone_number=value).exists():
                raise serializers.ValidationError("Phone number already exists. Please use a different number.")
        except Exception as e:
            # If there's a database error, log it but proceed
            print(f"Database error in validation: {e}")
            pass
        
        return value

    def validate(self, data):
        # Additional cross-field validation if needed
        return data

    def create(self, validated_data):
        try:
            return User.objects.create(**validated_data)
        except IntegrityError as e:
            if "duplicate key" in str(e) or "unique constraint" in str(e):
                raise serializers.ValidationError({
                    "phone_number": "Phone number already exists. Please use a different number."
                })
            raise serializers.ValidationError(f"Database error: {str(e)}")
        except Exception as e:
            raise serializers.ValidationError(f"Failed to create user: {str(e)}")

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=15,
        error_messages={
            'required': 'Phone number is required',
            'blank': 'Phone number cannot be empty',
            'max_length': 'Phone number cannot exceed 15 characters'
        }
    )

    def validate_phone_number(self, value):
        # Clean phone number
        value = ''.join(filter(str.isdigit, value))
        
        if len(value) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits")
        
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