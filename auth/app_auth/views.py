from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import User
from .serializers import (
    UserRegistrationSerializer, 
    UserProfileSerializer, 
    OTPVerifySerializer,
    OTPResendSerializer
)

class UserRegistrationView(generics.CreateAPIView):
    """Register a new user with phone number and password"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate token for user
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'success': True,
            'message': 'User registered successfully. Please verify your phone with OTP.',
            'user': UserProfileSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)

class OTPVerifyView(generics.GenericAPIView):
    """Verify user's phone number with OTP"""
    serializer_class = OTPVerifySerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get user
        user = User.objects.get(phone=serializer.validated_data['phone'])
        
        # Update token (optional - refresh token)
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'success': True,
            'message': 'Phone number verified successfully!',
            'user': UserProfileSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_200_OK)

class OTPResendView(generics.GenericAPIView):
    """Resend OTP to user's phone number"""
    serializer_class = OTPResendSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        otp = serializer.create_otp(serializer.validated_data)
        
        return Response({
            'success': True,
            'message': 'OTP has been resent to your phone number',
            'otp_code': otp.otp_code  # In production, don't return this
        }, status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get or update user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'data': serializer.data
        })

class UserLoginView(generics.GenericAPIView):
    """Login user with phone and password"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        phone = request.data.get('phone')
        password = request.data.get('password')
        
        if not phone or not password:
            return Response({
                'error': 'Phone and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid phone or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Authenticate user
        user_auth = authenticate(username=user.username, password=password)
        
        if not user_auth:
            return Response({
                'error': 'Invalid phone or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'user': UserProfileSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_200_OK)