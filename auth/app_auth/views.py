from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from .models import User
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer

class RegisterView(APIView):
    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.create(serializer.validated_data)
                response_serializer = UserSerializer(user)
                return Response({
                    "success": True,
                    "message": "User registered successfully",
                    "data": response_serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response({
                "success": False,
                "error": "Phone number already exists"
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.login_user()
                response_serializer = UserSerializer(user)
                return Response({
                    "success": True,
                    "message": "Login successful",
                    "data": response_serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserListView(APIView):
    def get(self, request):
        try:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response({
                "success": True,
                "count": users.count(),
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserDeleteView(APIView):
    def delete(self, request, user_id):
        try:
            user = get_object_or_404(User, id=user_id)
            user.delete()
            return Response({
                "success": True,
                "message": "User deleted successfully"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)