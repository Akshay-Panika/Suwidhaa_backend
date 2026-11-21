from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import CollegeCategory
from .serializers import CollegeCategorySerializer


# ═════════════════════════════════════════════
#  CREATE
# ═════════════════════════════════════════════
class CollegeCategoryCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = CollegeCategorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "College category created successfully",
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


# ═════════════════════════════════════════════
#  LIST
# ═════════════════════════════════════════════
class CollegeCategoryListView(APIView):

    def get(self, request):
        categories = CollegeCategory.objects.all().order_by("-id")
        serializer = CollegeCategorySerializer(categories, many=True)

        return Response(
            {
                "success": True,
                "count": categories.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ═════════════════════════════════════════════
#  DETAIL / UPDATE / DELETE
# ═════════════════════════════════════════════
class CollegeCategoryDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return CollegeCategory.objects.get(pk=pk)
        except CollegeCategory.DoesNotExist:
            return None

    def get(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response(
                {"success": False, "message": "College category not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"success": True, "data": CollegeCategorySerializer(category).data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response(
                {"success": False, "message": "College category not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CollegeCategorySerializer(category, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "College category updated successfully",
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
        category = self.get_object(pk)
        if not category:
            return Response(
                {"success": False, "message": "College category not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CollegeCategorySerializer(
            category, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "College category updated successfully",
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
        category = self.get_object(pk)
        if not category:
            return Response(
                {"success": False, "message": "College category not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        category.delete()
        return Response(
            {
                "success": True,
                "message": "College category deleted successfully",
            },
            status=status.HTTP_200_OK,
        )