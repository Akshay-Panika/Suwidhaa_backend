from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db import IntegrityError, transaction
from .models import EcommerceProduct, EcommerceFavorite
from .serializers import EcommerceProductSerializer
from auth.app_auth.models import User

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
                    {"success": False, "message": "Database error."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {
                    "success": True,
                    "message": "Product created successfully",
                    "data": EcommerceProductSerializer(
                        product, context={"request": request}
                    ).data,
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


# ══════════════════════════════════════════════
# LISTS
# ══════════════════════════════════════════════

class EcommerceProductAllView(APIView):
    """
    GET /api/v1/ecommerce/product/all/
    Saare products — koi user context nahi.
    Filters: ?category=<id>&subcategory=<id>&search=<text>
    """

    def get(self, request):
        products = (
            EcommerceProduct.objects
            .select_related("subcategory", "subcategory__category", "user")
            .prefetch_related("images")
            .all()
            .order_by("-id")
        )

        subcategory_id = request.query_params.get("subcategory")
        if subcategory_id:
            products = products.filter(subcategory_id=subcategory_id)

        category_id = request.query_params.get("category")
        if category_id:
            products = products.filter(subcategory__category_id=category_id)

        search = request.query_params.get("search")
        if search:
            products = products.filter(title__icontains=search)

        serializer = EcommerceProductSerializer(
            products, many=True, context={"request": request}
        )

        return Response(
            {
                "success": True,
                "count": products.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class EcommerceProductOwnerView(APIView):
    """
    GET /api/v1/ecommerce/product/owner/<user_id>/
    Us user ne jo products upload kiye hain.
    Filters: ?category=<id>&subcategory=<id>&search=<text>
    """

    def get(self, request, user_id):
        try:
            user_obj = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"success": False, "message": f"User {user_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        products = (
            EcommerceProduct.objects
            .select_related("subcategory", "subcategory__category", "user")
            .prefetch_related("images")
            .filter(user_id=user_id)
            .order_by("-id")
        )

        subcategory_id = request.query_params.get("subcategory")
        if subcategory_id:
            products = products.filter(subcategory_id=subcategory_id)

        category_id = request.query_params.get("category")
        if category_id:
            products = products.filter(subcategory__category_id=category_id)

        search = request.query_params.get("search")
        if search:
            products = products.filter(title__icontains=search)

        serializer = EcommerceProductSerializer(
            products, many=True, context={"request": request}
        )

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


class EcommerceProductFeedView(APIView):
    """
    GET /api/v1/ecommerce/product/feed/<user_id>/
    Saare products, is user ke perspective se is_favorite true/false.
    Filters: ?category=<id>&subcategory=<id>&search=<text>
    """

    def get(self, request, user_id):
        try:
            user_obj = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"success": False, "message": f"User {user_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        products = (
            EcommerceProduct.objects
            .select_related("subcategory", "subcategory__category", "user")
            .prefetch_related("images")
            .all()
            .order_by("-id")
        )

        subcategory_id = request.query_params.get("subcategory")
        if subcategory_id:
            products = products.filter(subcategory_id=subcategory_id)

        category_id = request.query_params.get("category")
        if category_id:
            products = products.filter(subcategory__category_id=category_id)

        search = request.query_params.get("search")
        if search:
            products = products.filter(title__icontains=search)

        # user_id serializer ko pass karo (is_favorite ke liye)
        request.query_params._mutable = True
        request.query_params["user"] = str(user_id)

        serializer = EcommerceProductSerializer(
            products, many=True, context={"request": request}
        )

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



class EcommerceFavoriteListView(APIView):
    """
    GET /api/v1/ecommerce/product/favorites/<user_id>/
    User ke favorite products.
    """

    def get(self, request, user_id):
        try:
            user_obj = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"success": False, "message": f"User {user_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        products = (
            EcommerceProduct.objects
            .select_related("subcategory", "subcategory__category", "user")
            .prefetch_related("images")
            .filter(favorites__user=user_obj)
            .order_by("-id")
        )

        # is_favorite ke liye user_id query param mein daalo
        request.query_params._mutable = True
        request.query_params["user"] = str(user_id)

        serializer = EcommerceProductSerializer(
            products, many=True, context={"request": request}
        )

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


class EcommerceFavoriteToggleView(APIView):
    """
    PATCH /api/v1/ecommerce/product/<pk>/favorite/toggle/?user=<user_id>
    Favorite add/remove toggle.
    """

    def patch(self, request, pk):
        user_id = request.query_params.get("user")
        if not user_id:
            return Response(
                {"success": False, "message": "user query param is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_obj = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"success": False, "message": f"User {user_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            product = EcommerceProduct.objects.get(pk=pk)
        except EcommerceProduct.DoesNotExist:
            return Response(
                {"success": False, "message": "Product not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        fav = EcommerceFavorite.objects.filter(
            user=user_obj, product=product
        ).first()

        if fav:
            fav.delete()
            return Response(
                {
                    "success": True,
                    "message": "Removed from favorites",
                    "data": {"product_id": product.id, "is_favorite": False},
                },
                status=status.HTTP_200_OK,
            )
        else:
            EcommerceFavorite.objects.create(user=user_obj, product=product)
            return Response(
                {
                    "success": True,
                    "message": "Added to favorites",
                    "data": {"product_id": product.id, "is_favorite": True},
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
                {"success": False, "message": "Product not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {
                "success": True,
                "data": EcommerceProductSerializer(
                    product, context={"request": request}
                ).data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response(
                {"success": False, "message": "Product not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EcommerceProductSerializer(product, data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    product = serializer.save()
            except IntegrityError:
                return Response(
                    {"success": False, "message": "Database error."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {
                    "success": True,
                    "message": "Product updated successfully",
                    "data": EcommerceProductSerializer(
                        product, context={"request": request}
                    ).data,
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
                {"success": False, "message": "Product not found"},
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
                    {"success": False, "message": "Database error."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {
                    "success": True,
                    "message": "Product updated successfully",
                    "data": EcommerceProductSerializer(
                        product, context={"request": request}
                    ).data,
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
                {"success": False, "message": "Product not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        product.delete()
        return Response(
            {"success": True, "message": "Product deleted successfully"},
            status=status.HTTP_200_OK,
        )