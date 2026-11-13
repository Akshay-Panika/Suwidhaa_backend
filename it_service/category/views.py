from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Case, When, Value, IntegerField

from .models import ItServiceCategory
from .serializers import ItServiceCategorySerializer


class ItServiceCategoryCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = ItServiceCategorySerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Category created successfully",
                    "data": ItServiceCategorySerializer(category).data,
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


class ItServiceCategoryListView(APIView):
    def get(self, request):
        # 1) Make sure the built-in "All" row exists (and is named correctly)
        ItServiceCategory.ensure_default()

        # 2) id=0 ("All") ko hamesha sabse pehle dikhane ke liye
        categories = (
            ItServiceCategory.objects.annotate(
                priority=Case(
                    When(id=ItServiceCategory.ALL_SERVICES_ID, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            ).order_by("priority", "-id")
        )
        data = ItServiceCategorySerializer(categories, many=True).data

        # 3) Safety net: ALWAYS prepend "All" if somehow missing
        if not any(item.get("id") == ItServiceCategory.ALL_SERVICES_ID for item in data):
            data.insert(
                0,
                {
                    "id": ItServiceCategory.ALL_SERVICES_ID,
                    "name": ItServiceCategory.ALL_SERVICES_NAME,   # "All"
                    "image": None,
                    "is_default": True,
                    "created_at": None,
                    "updated_at": None,
                },
            )

        return Response(
            {
                "success": True,
                "count": len(data),
                "data": data,
            },
            status=status.HTTP_200_OK,
        )


class ItServiceCategoryDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return ItServiceCategory.objects.get(pk=pk)
        except ItServiceCategory.DoesNotExist:
            return None

    def get(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response(
                {"success": False, "message": "Category not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"success": True, "data": ItServiceCategorySerializer(category).data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response(
                {"success": False, "message": "Category not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = ItServiceCategorySerializer(category, data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Category updated successfully",
                    "data": ItServiceCategorySerializer(category).data,
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
                {"success": False, "message": "Category not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = ItServiceCategorySerializer(
            category, data=request.data, partial=True
        )
        if serializer.is_valid():
            category = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Category updated successfully",
                    "data": ItServiceCategorySerializer(category).data,
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
                {"success": False, "message": "Category not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if category.is_default:
            return Response(
                {
                    "success": False,
                    "message": "The 'All' category cannot be deleted.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        category.delete()
        return Response(
            {"success": True, "message": "Category deleted successfully"},
            status=status.HTTP_200_OK,
        )