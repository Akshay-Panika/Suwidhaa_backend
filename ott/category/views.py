from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from .models import Category
from .serializers import CategorySerializer


# ✅ Virtual "All Content" — always returned as first item (not stored in DB)
ALL_CONTENT_VIRTUAL = {
    "id": 0,
    "name": "All Content",
    "image": "",
    "category_type": "all",
    "is_active": True,
    "created_at": None,
    "updated_at": None,
}


class CategoryListCreateAPIView(APIView):
    """GET: List all categories (with All Content first) | POST: Create a new category"""

    def get(self, request):
        try:
            categories = Category.objects.all().order_by("created_at")
            serializer = CategorySerializer(categories, many=True)

            data = [ALL_CONTENT_VIRTUAL] + list(serializer.data)

            return Response(
                {
                    "success": True,
                    "count": len(data),
                    "data": data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # ✅ POST — THIS WAS MISSING
    def post(self, request):
        try:
            serializer = CategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "success": True,
                        "message": "Category created successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except IntegrityError:
            return Response(
                {"success": False, "error": "Category name already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CategoryDetailAPIView(APIView):
    """GET | PUT | DELETE a single category"""

    def get_object(self, pk):
        return get_object_or_404(Category, pk=pk)

    def get(self, request, pk):
        try:
            if pk == 0:
                return Response(
                    {"success": True, "data": ALL_CONTENT_VIRTUAL},
                    status=status.HTTP_200_OK,
                )
            category = self.get_object(pk)
            serializer = CategorySerializer(category)
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Category.DoesNotExist:
            return Response(
                {"success": False, "error": "Category not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, pk):
        try:
            if pk == 0:
                return Response(
                    {
                        "success": False,
                        "error": 'Cannot update the "All Content" category',
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            category = self.get_object(pk)
            serializer = CategorySerializer(
                category, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "success": True,
                        "message": "Category updated successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Category.DoesNotExist:
            return Response(
                {"success": False, "error": "Category not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except IntegrityError:
            return Response(
                {"success": False, "error": "Category name already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, pk):
        try:
            if pk == 0:
                return Response(
                    {
                        "success": False,
                        "error": 'Cannot delete the "All Content" category',
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            category = self.get_object(pk)
            category.delete()
            return Response(
                {"success": True, "message": "Category deleted successfully"},
                status=status.HTTP_200_OK,
            )
        except Category.DoesNotExist:
            return Response(
                {"success": False, "error": "Category not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )