from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db import IntegrityError

from .models import EcommerceCategory
from .serializers import EcommerceCategorySerializer


class EcommerceCategoryCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = EcommerceCategorySerializer(data=request.data)

        if serializer.is_valid():
            try:
                category = serializer.save()
            except IntegrityError:
                return Response(
                    {
                        "success": False,
                        "message": "This category already exists.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {
                    "success": True,
                    "message": "Ecommerce category created successfully",
                    "data": EcommerceCategorySerializer(category).data,
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


class EcommerceCategoryListView(APIView):

    def get(self, request):
        categories = EcommerceCategory.objects.all().order_by("-id")
        serializer = EcommerceCategorySerializer(categories, many=True)

        return Response(
            {
                "success": True,
                "count": categories.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class EcommerceCategoryDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return EcommerceCategory.objects.get(pk=pk)
        except EcommerceCategory.DoesNotExist:
            return None

    def get(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response(
                {"success": False, "message": "Ecommerce category not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"success": True, "data": EcommerceCategorySerializer(category).data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response(
                {"success": False, "message": "Ecommerce category not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EcommerceCategorySerializer(category, data=request.data)

        if serializer.is_valid():
            try:
                category = serializer.save()
            except IntegrityError:
                return Response(
                    {
                        "success": False,
                        "message": "This category already exists.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {
                    "success": True,
                    "message": "Ecommerce category updated successfully",
                    "data": EcommerceCategorySerializer(category).data,
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
        category = self.get_object(pk)
        if not category:
            return Response(
                {"success": False, "message": "Ecommerce category not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EcommerceCategorySerializer(
            category, data=request.data, partial=True
        )

        if serializer.is_valid():
            try:
                category = serializer.save()
            except IntegrityError:
                return Response(
                    {
                        "success": False,
                        "message": "This category already exists.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {
                    "success": True,
                    "message": "Ecommerce category updated successfully",
                    "data": EcommerceCategorySerializer(category).data,
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
        category = self.get_object(pk)
        if not category:
            return Response(
                {"success": False, "message": "Ecommerce category not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        category.delete()
        return Response(
            {
                "success": True,
                "message": "Ecommerce category deleted successfully",
            },
            status=status.HTTP_200_OK,
        )