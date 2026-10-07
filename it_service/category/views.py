from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

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
                    "message": "IT service category created successfully",
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
        categories = ItServiceCategory.objects.all().order_by("-id")
        serializer = ItServiceCategorySerializer(categories, many=True)

        return Response(
            {
                "success": True,
                "count": categories.count(),
                "data": serializer.data,
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
                {"success": False, "message": "IT service category not found"},
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
                {"success": False, "message": "IT service category not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ItServiceCategorySerializer(category, data=request.data)

        if serializer.is_valid():
            category = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "IT service category updated successfully",
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
                {"success": False, "message": "IT service category not found"},
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
                    "message": "IT service category updated successfully",
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
                {"success": False, "message": "IT service category not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        category.delete()
        return Response(
            {
                "success": True,
                "message": "IT service category deleted successfully",
            },
            status=status.HTTP_200_OK,
        )