from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db import IntegrityError

from .models import EcommerceStore
from .serializers import EcommerceStoreSerializer
from auth.app_auth.models import User


class EcommerceStoreCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = EcommerceStoreSerializer(data=request.data)

        if serializer.is_valid():
            try:
                store = serializer.save()
            except IntegrityError:
                return Response(
                    {"success": False, "message": "Database error. Store could not be saved."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {
                    "success": True,
                    "message": "Store created successfully",
                    "data": EcommerceStoreSerializer(store).data,
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


class EcommerceStoreDetailByUserView(APIView):
    """
    GET /api/v1/ecommerce/store/user/<user_id>/
    User ka store check karne aur detail nikalne ke liye.
    """

    def get(self, request, user_id):
        try:
            store = EcommerceStore.objects.select_related("user").get(user_id=user_id)
        except EcommerceStore.DoesNotExist:
            return Response(
                {"success": False, "message": "No store found for this user", "has_store": False},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "success": True,
                "has_store": True,
                "data": EcommerceStoreSerializer(store).data,
            },
            status=status.HTTP_200_OK,
        )


class EcommerceStoreListView(APIView):
    """
    GET /api/v1/ecommerce/store/list/
    Saare stores list karne ke liye.
    Filters: ?category=fashion
    """

    def get(self, request):
        stores = EcommerceStore.objects.select_related("user").all().order_by("-id")

        # Filter by category
        category = request.query_params.get("category")
        if category:
            stores = stores.filter(store_category=category)

        serializer = EcommerceStoreSerializer(stores, many=True)

        return Response(
            {
                "success": True,
                "count": stores.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class EcommerceStoreDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return EcommerceStore.objects.select_related("user").get(pk=pk)
        except EcommerceStore.DoesNotExist:
            return None

    def get(self, request, pk):
        store = self.get_object(pk)
        if not store:
            return Response(
                {"success": False, "message": "Store not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"success": True, "data": EcommerceStoreSerializer(store).data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        store = self.get_object(pk)
        if not store:
            return Response(
                {"success": False, "message": "Store not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EcommerceStoreSerializer(store, data=request.data)

        if serializer.is_valid():
            try:
                store = serializer.save()
            except IntegrityError:
                return Response(
                    {"success": False, "message": "Database error. Store could not be updated."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {
                    "success": True,
                    "message": "Store updated successfully",
                    "data": EcommerceStoreSerializer(store).data,
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
        store = self.get_object(pk)
        if not store:
            return Response(
                {"success": False, "message": "Store not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EcommerceStoreSerializer(store, data=request.data, partial=True)

        if serializer.is_valid():
            try:
                store = serializer.save()
            except IntegrityError:
                return Response(
                    {"success": False, "message": "Database error. Store could not be updated."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {
                    "success": True,
                    "message": "Store updated successfully",
                    "data": EcommerceStoreSerializer(store).data,
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
        store = self.get_object(pk)
        if not store:
            return Response(
                {"success": False, "message": "Store not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        store.delete()
        return Response(
            {"success": True, "message": "Store deleted successfully"},
            status=status.HTTP_200_OK,
        )