from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
import logging
from .models import User
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer

# Set up logging
logger = logging.getLogger(__name__)

class RegisterView(APIView):
    """
    Register a new user
    """
    def post(self, request):
        try:
            # Log incoming request data (excluding sensitive info)
            logger.info(f"Registration attempt for phone: {request.data.get('phone_number', 'unknown')}")
            
            serializer = RegisterSerializer(data=request.data)
            
            if serializer.is_valid():
                try:
                    user = serializer.create(serializer.validated_data)
                    response_serializer = UserSerializer(user)
                    logger.info(f"User registered successfully: {user.phone_number}")
                    return Response(
                        {
                            "success": True,
                            "message": "User registered successfully",
                            "data": response_serializer.data
                        },
                        status=status.HTTP_201_CREATED
                    )
                except IntegrityError as e:
                    logger.error(f"Integrity error: {str(e)}")
                    return Response(
                        {
                            "success": False,
                            "error": "Database error occurred"
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                logger.warning(f"Validation errors: {serializer.errors}")
                return Response(
                    {
                        "success": False,
                        "errors": serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Unexpected error in RegisterView: {str(e)}")
            return Response(
                {
                    "success": False,
                    "error": "An unexpected error occurred"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LoginView(APIView):
    """
    Login a user
    """
    def post(self, request):
        try:
            logger.info(f"Login attempt for phone: {request.data.get('phone_number', 'unknown')}")
            
            serializer = LoginSerializer(data=request.data)
            
            if serializer.is_valid():
                try:
                    user = serializer.login_user()
                    response_serializer = UserSerializer(user)
                    logger.info(f"User logged in successfully: {user.phone_number}")
                    return Response(
                        {
                            "success": True,
                            "message": "Login successful",
                            "data": response_serializer.data
                        },
                        status=status.HTTP_200_OK
                    )
                except User.DoesNotExist:
                    return Response(
                        {
                            "success": False,
                            "error": "User not found"
                        },
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                logger.warning(f"Login validation errors: {serializer.errors}")
                return Response(
                    {
                        "success": False,
                        "errors": serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Unexpected error in LoginView: {str(e)}")
            return Response(
                {
                    "success": False,
                    "error": "An unexpected error occurred"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserListView(APIView):
    """
    Get all users
    """
    def get(self, request):
        try:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(
                {
                    "success": True,
                    "count": users.count(),
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error in UserListView: {str(e)}")
            return Response(
                {
                    "success": False,
                    "error": "Failed to fetch users"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserDeleteView(APIView):
    """
    Delete a user by ID
    """
    def delete(self, request, user_id):
        try:
            user = get_object_or_404(User, id=user_id)
            user_name = user.name
            user.delete()
            logger.info(f"User deleted: {user_name} (ID: {user_id})")
            return Response(
                {
                    "success": True,
                    "message": f"User '{user_name}' deleted successfully"
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error in UserDeleteView: {str(e)}")
            return Response(
                {
                    "success": False,
                    "error": "Failed to delete user"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )