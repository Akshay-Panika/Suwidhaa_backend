from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import NgoStaff
from .serializers import NgoStaffSerializer


class NgoStaffCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = NgoStaffSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "NGO staff created successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "message": "Validation failed",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class NgoStaffListView(APIView):
    def get(self, request):
        staff = NgoStaff.objects.all()
        serializer = NgoStaffSerializer(staff, many=True)

        return Response(
            {
                "success": True,
                "count": len(serializer.data),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class NgoStaffDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        return get_object_or_404(NgoStaff, pk=pk)

    def get(self, request, pk):
        staff = self.get_object(pk)
        return Response(
            {
                "success": True,
                "data": NgoStaffSerializer(staff).data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        staff = self.get_object(pk)
        serializer = NgoStaffSerializer(staff, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "NGO staff updated successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Validation failed",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        staff = self.get_object(pk)
        serializer = NgoStaffSerializer(
            staff,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "NGO staff updated successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Validation failed",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        staff = self.get_object(pk)
        staff.delete()
        return Response(
            {
                "success": True,
                "message": "NGO staff deleted successfully",
            },
            status=status.HTTP_200_OK,
        )