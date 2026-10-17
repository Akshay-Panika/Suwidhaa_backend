from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db import IntegrityError, transaction

from .models import EcommerceProduct
from .serializers import EcommerceProductSerializer


class EcommerceProductCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = EcommerceProductSerializer(data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    product = serializer.save()
            except IntegrityError:
                return Response(
                    {
                        "success": False,
                        "message": "Database error. Product could not be saved.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {
                    "success": True,
                    "message": "Ecommerce product created successfully",
                    "data": EcommerceProductSerializer(product).data,
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


class EcommerceProductListView(APIView):

    def get(self, request):
        products = EcommerceProduct.objects.select_related(
            "subcategory", "subcategory__category", "user"
        ).prefetch_related("images").all().order_by("-id")

        # Filters
        subcategory_id = request.query_params.get("subcategory")
        if subcategory_id:
            products = products.filter(subcategory_id=subcategory_id)

        category_id = request.query_params.get("category")
        if category_id:
            products = products.filter(subcategory__category_id=category_id)

        user_id = request.query_params.get("user")
        if user_id:
            products = products.filter(user_id=user_id)

        is_active = request.query_params.get("active")
        if is_active is not None:
            products = products.filter(is_active=is_active.lower() == "true")

        search = request.query_params.get("search")
        if search:
            products = products.filter(title__icontains=search)

        serializer = EcommerceProductSerializer(products, many=True)

        return Response(
            {
                "success": True,
                "count": products.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class EcommerceProductDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return EcommerceProduct.objects.select_related(
                "subcategory", "subcategory__category", "user"
            ).prefetch_related("images").get(pk=pk)
        except EcommerceProduct.DoesNotExist:
            return None

    def get(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response(
                {"success": False, "message": "Ecommerce product not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"success": True, "data": EcommerceProductSerializer(product).data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response(
                {"success": False, "message": "Ecommerce product not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EcommerceProductSerializer(product, data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    product = serializer.save()
            except IntegrityError:
                return Response(
                    {
                        "success": False,
                        "message": "Database error. Product could not be updated.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {
                    "success": True,
                    "message": "Ecommerce product updated successfully",
                    "data": EcommerceProductSerializer(product).data,
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
        product = self.get_object(pk)
        if not product:
            return Response(
                {"success": False, "message": "Ecommerce product not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EcommerceProductSerializer(
            product, data=request.data, partial=True
        )

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    product = serializer.save()
            except IntegrityError:
                return Response(
                    {
                        "success": False,
                        "message": "Database error. Product could not be updated.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {
                    "success": True,
                    "message": "Ecommerce product updated successfully",
                    "data": EcommerceProductSerializer(product).data,
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
        product = self.get_object(pk)
        if not product:
            return Response(
                {"success": False, "message": "Ecommerce product not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        product.delete()
        return Response(
            {
                "success": True,
                "message": "Ecommerce product deleted successfully",
            },
            status=status.HTTP_200_OK,
        )

class EcommerceProductByUserListView(APIView):
    """
    Ek user ke saare products return karta hai.
    URL: /api/v1/ecommerce/product/user/<user_id>/
    """

    def get(self, request, user_id):
        # User exist karta hai ya nahi check karo
        try:
            user_obj = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": f"User with ID {user_id} not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        products = (
            EcommerceProduct.objects
            .select_related("subcategory", "subcategory__category", "user")
            .prefetch_related("images")
            .filter(user_id=user_id)
            .order_by("-id")
        )

        # Optional filters
        is_active = request.query_params.get("active")
        if is_active is not None:
            products = products.filter(is_active=is_active.lower() == "true")

        subcategory_id = request.query_params.get("subcategory")
        if subcategory_id:
            products = products.filter(subcategory_id=subcategory_id)

        search = request.query_params.get("search")
        if search:
            products = products.filter(title__icontains=search)

        serializer = EcommerceProductSerializer(products, many=True)

        return Response(
            {
                "success": True,
                "user": {
                    "id": user_obj.id,
                    "name": user_obj.name,
                    "phone_number": user_obj.phone_number,
                },
                "count": products.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )    