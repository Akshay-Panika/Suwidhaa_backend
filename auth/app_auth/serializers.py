from rest_framework import serializers
from .models import User, OTP
from django.contrib.auth.password_validation import validate_password
import re

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'email', 'profile_image', 'address', 'password', 'confirm_password']
        extra_kwargs = {
            'username': {'required': True},
            'phone': {'required': True},
            'profile_image': {'required': False, 'allow_null': True},
            'email': {'required': False, 'allow_blank': True},
            'address': {'required': False, 'allow_blank': True}
        }
    
    def validate_phone(self, value):
        """Validate phone number format"""
        if not re.match(r'^[0-9]{10,15}$', value):
            raise serializers.ValidationError("Phone number must be 10-15 digits")
        return value
    
    def validate(self, data):
        """Validate password match"""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})
        
        # Check if phone already exists
        if User.objects.filter(phone=data['phone']).exists():
            raise serializers.ValidationError({"phone": "This phone number is already registered"})
        
        # Check if username already exists
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "This username is already taken"})
        
        return data
    
    def create(self, validated_data):
        """Create user and generate OTP"""
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        
        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            phone=validated_data['phone'],
            password=password,
            email=validated_data.get('email', ''),
            profile_image=validated_data.get('profile_image', None),
            address=validated_data.get('address', '')
        )
        
        # Generate OTP
        from datetime import datetime, timedelta
        import random
        
        otp_code = ''.join(random.choices('0123456789', k=6))
        expires_at = datetime.now() + timedelta(minutes=10)
        
        OTP.objects.create(
            user=user,
            otp_code=otp_code,
            expires_at=expires_at
        )
        
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'email', 'profile_image', 'address', 'is_phone_verified']
        read_only_fields = ['id', 'is_phone_verified']
        extra_kwargs = {
            'profile_image': {'required': False, 'allow_null': True},
            'email': {'required': False, 'allow_blank': True},
            'address': {'required': False, 'allow_blank': True}
        }

class OTPVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    otp_code = serializers.CharField(required=True, max_length=6)
    
    def validate(self, data):
        """Validate OTP"""
        try:
            user = User.objects.get(phone=data['phone'])
        except User.DoesNotExist:
            raise serializers.ValidationError({"phone": "User with this phone number does not exist"})
        
        try:
            otp_obj = OTP.objects.filter(user=user, is_used=False).latest('created_at')
        except OTP.DoesNotExist:
            raise serializers.ValidationError({"otp_code": "No active OTP found for this user"})
        
        # Check if OTP is expired
        from django.utils import timezone
        if otp_obj.expires_at < timezone.now():
            raise serializers.ValidationError({"otp_code": "OTP has expired. Please request a new one"})
        
        # Check if OTP matches
        if otp_obj.otp_code != data['otp_code']:
            raise serializers.ValidationError({"otp_code": "Invalid OTP"})
        
        # Mark OTP as used
        otp_obj.is_used = True
        otp_obj.save()
        
        # Mark user as verified
        user.is_phone_verified = True
        user.save()
        
        return data

class OTPResendSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    
    def validate_phone(self, value):
        """Validate phone number"""
        try:
            user = User.objects.get(phone=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this phone number does not exist")
        return value
    
    def create_otp(self, validated_data):
        """Generate new OTP for user"""
        user = User.objects.get(phone=validated_data['phone'])
        
        from datetime import datetime, timedelta
        import random
        
        otp_code = ''.join(random.choices('0123456789', k=6))
        expires_at = datetime.now() + timedelta(minutes=10)
        
        otp = OTP.objects.create(
            user=user,
            otp_code=otp_code,
            expires_at=expires_at
        )
        
        return otp