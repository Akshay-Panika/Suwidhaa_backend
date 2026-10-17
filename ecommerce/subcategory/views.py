from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db import IntegrityError

from .models import EcommerceSubcategory
from .serializers import EcommerceSubcategorySerializer


class EcommerceSubcategoryCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = EcommerceSubcategorySerializer(data=request.data)

        if serializer.is_valid():
            try:
                subcategory = serializer.save()
            except IntegrityError:
                return Response(
                    {
                        "success": False,
                        "message": "This subcategory already exists in this category.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {
                    "success": True,
                    "message": "Ecommerce subcategory created successfully",
                    "data": EcommerceSubcategorySerializer(subcategory).data,
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


class EcommerceSubcategoryListView(APIView):

    def get(self, request):
        subcategories = EcommerceSubcategory.objects.select_related(
            "category"
        ).all().order_by("-id")

        # optional filter: ?category=<id>
        category_id = request.query_params.get("category")
        if category_id:
            subcategories = subcategories.filter(category_id=category_id)

        serializer = EcommerceSubcategorySerializer(subcategories, many=True)

        return Response(
            {
                "success": True,
                "count": subcategories.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class EcommerceSubcategoryDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return EcommerceSubcategory.objects.select_related("category").get(pk=pk)
        except EcommerceSubcategory.DoesNotExist:
            return None

    def get(self, request, pk):
        subcategory = self.get_object(pk)
        if not subcategory:
            return Response(
                {"success": False, "message": "Ecommerce subcategory not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"success": True, "data": EcommerceSubcategorySerializer(subcategory).data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        subcategory = self.get_object(pk)
        if not subcategory:
            return Response(
                {"success": False, "message": "Ecommerce subcategory not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EcommerceSubcategorySerializer(subcategory, data=request.data)

        if serializer.is_valid():
            try:
                subcategory = serializer.save()
            except IntegrityError:
                return Response(
                    {
                        "success": False,
                        "message": "This subcategory already exists in this category.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {
                    "success": True,
                    "message": "Ecommerce subcategory updated successfully",
                    "data": EcommerceSubcategorySerializer(subcategory).data,
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
        subcategory = self.get_object(pk)
        if not subcategory:
            return Response(
                {"success": False, "message": "Ecommerce subcategory not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EcommerceSubcategorySerializer(
            subcategory, data=request.data, partial=True
        )

        if serializer.is_valid():
            try:
                subcategory = serializer.save()
            except IntegrityError:
                return Response(
                    {
                        "success": False,
                        "message": "This subcategory already exists in this category.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {
                    "success": True,
                    "message": "Ecommerce subcategory updated successfully",
                    "data": EcommerceSubcategorySerializer(subcategory).data,
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
        subcategory = self.get_object(pk)
        if not subcategory:
            return Response(
                {"success": False, "message": "Ecommerce subcategory not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        subcategory.delete()
        return Response(
            {
                "success": True,
                "message": "Ecommerce subcategory deleted successfully",
            },
            status=status.HTTP_200_OK,
        )