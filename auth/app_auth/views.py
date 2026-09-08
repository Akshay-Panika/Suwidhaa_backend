from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db import connection
from .models import User
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer

class RegisterView(APIView):
    def post(self, request):
        try:
            # First, check if the table exists and has the correct columns
            with connection.cursor() as cursor:
                try:
                    cursor.execute("SELECT 1 FROM app_auth_user LIMIT 1")
                except Exception as e:
                    return Response({
                        "success": False,
                        "error": "Database table issue. Please contact support."
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.create(serializer.validated_data)
                response_serializer = UserSerializer(user)
                return Response({
                    "success": True,
                    "message": "User registered successfully",
                    "data": response_serializer.data
                }, status=status.HTTP_201_CREATED)
            
            # Return validation errors cleanly
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except IntegrityError as e:
            error_msg = str(e)
            # Handle duplicate phone number error
            if "duplicate key" in error_msg or "unique constraint" in error_msg or "phone_number" in error_msg:
                return Response({
                    "success": False,
                    "error": "Phone number already exists. Please use a different phone number."
                }, status=status.HTTP_400_BAD_REQUEST)
            # Handle other integrity errors
            return Response({
                "success": False,
                "error": "Database error occurred. Please try again."
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            # Return a clean error message for any other errors
            return Response({
                "success": False,
                "error": "An unexpected error occurred. Please try again."
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
            
        except User.DoesNotExist:
            return Response({
                "success": False,
                "error": "User not found with this phone number"
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                "success": False,
                "error": "An unexpected error occurred during login"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserListView(APIView):
    def get(self, request):
        try:
            # Check if table exists first
            with connection.cursor() as cursor:
                try:
                    cursor.execute("SELECT 1 FROM app_auth_user LIMIT 1")
                except Exception as e:
                    return Response({
                        "success": False,
                        "error": "Database table issue. Please contact support."
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
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
                "error": "Failed to fetch users. Please try again."
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
            
        except User.DoesNotExist:
            return Response({
                "success": False,
                "error": f"User with ID {user_id} not found"
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                "success": False,
                "error": "Failed to delete user. Please try again."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)