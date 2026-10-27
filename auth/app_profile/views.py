from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404

from auth.app_auth.models import User
from .models import UserProfile
from .serializers import UserProfileSerializer


class UserProfileListView(APIView):
    """Get all profiles list"""
    def get(self, request):
        profiles = UserProfile.objects.select_related('user').all().order_by('-id')
        serializer = UserProfileSerializer(profiles, many=True)
        return Response(
            {
                "success": True,
                "count": profiles.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class UserProfileDetailView(APIView):
    """Get single profile by ID"""
    def get(self, request, profile_id):
        try:
            profile = UserProfile.objects.select_related('user').get(id=profile_id)
            return Response(
                {"success": True, "data": UserProfileSerializer(profile).data},
                status=status.HTTP_200_OK,
            )
        except UserProfile.DoesNotExist:
            return Response(
                {"success": False, "message": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


class UserProfileCreateUpdateView(APIView):
    """Create or Update profile for a specific User ID"""
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"success": False, "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if profile exists for this user
        profile = UserProfile.objects.filter(user=user).first()

        if profile:
            # Update existing profile
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
            message = "Profile updated successfully"
            response_status = status.HTTP_200_OK
        else:
            # Create new profile
            serializer = UserProfileSerializer(data=request.data)
            message = "Profile created successfully"
            response_status = status.HTTP_201_CREATED

        if serializer.is_valid():
            # Set the user manually if creating new
            if not profile:
                serializer.save(user=user)
            else:
                serializer.save()

            return Response(
                {
                    "success": True,
                    "message": message,
                    "data": serializer.data,
                },
                status=response_status,
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserProfileDeleteView(APIView):
    """Delete a profile by ID"""
    def delete(self, request, profile_id):
        try:
            profile = UserProfile.objects.get(id=profile_id)
            profile.delete()
            return Response(
                {"success": True, "message": "Profile deleted successfully"},
                status=status.HTTP_200_OK,
            )
        except UserProfile.DoesNotExist:
            return Response(
                {"success": False, "message": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND,
            )