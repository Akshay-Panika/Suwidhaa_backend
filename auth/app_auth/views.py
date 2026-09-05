from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer

class RegisterView(APIView):
    def post(self, request):
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

class LoginView(APIView):
    def post(self, request):
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

class UserListView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response({
            "success": True,
            "count": users.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class UserDeleteView(APIView):
    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return Response({
            "success": True,
            "message": f"User deleted successfully"
        }, status=status.HTTP_200_OK)