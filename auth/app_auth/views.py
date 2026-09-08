from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db import connection
from .models import User
from .serializers import UserSerializer  # Only import UserSerializer

class RegisterView(APIView):
    """This view handles both registration and login"""
    def post(self, request):
        try:
            # Check if table exists
            with connection.cursor() as cursor:
                try:
                    cursor.execute("SELECT 1 FROM app_auth_user LIMIT 1")
                except Exception as e:
                    return Response({
                        "success": False,
                        "error": "Database table issue. Please contact support."
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Get phone number from request
            phone_number = request.data.get('phone_number', '').strip()
            name = request.data.get('name', '').strip()
            
            if not phone_number:
                return Response({
                    "success": False,
                    "error": "Phone number is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Clean phone number (remove spaces, special characters)
            cleaned_phone = ''.join(filter(str.isdigit, phone_number))
            
            if len(cleaned_phone) < 10:
                return Response({
                    "success": False,
                    "error": "Phone number must be at least 10 digits"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if user exists
            user = User.objects.filter(phone_number=cleaned_phone).first()
            
            if user:
                # User exists - LOGIN
                user.is_logged_in = True
                user.save()
                response_serializer = UserSerializer(user)
                return Response({
                    "success": True,
                    "message": "Login successful",
                    "action": "login",
                    "data": response_serializer.data
                }, status=status.HTTP_200_OK)
            else:
                # User doesn't exist - REGISTER
                if not name:
                    return Response({
                        "success": False,
                        "error": "Name is required for new registration"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Create new user
                user = User.objects.create(
                    name=name,
                    phone_number=cleaned_phone,
                    is_logged_in=True  # Auto login after registration
                )
                response_serializer = UserSerializer(user)
                return Response({
                    "success": True,
                    "message": "User registered and logged in successfully",
                    "action": "register",
                    "data": response_serializer.data
                }, status=status.HTTP_201_CREATED)
                
        except IntegrityError as e:
            return Response({
                "success": False,
                "error": "Database error occurred. Please try again."
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "success": False,
                "error": "An unexpected error occurred. Please try again."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserListView(APIView):
    """Get all users list"""
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
    """Delete a user by ID"""
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