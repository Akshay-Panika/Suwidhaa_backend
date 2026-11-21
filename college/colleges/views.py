from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import models

from .models import College, CollegeImage
from .serializers import CollegeSerializer
from college.category.models import CollegeCategory


# ═════════════════════════════════════════════
#  CREATE
# ═════════════════════════════════════════════
class CollegeCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        name = request.data.get("name")
        address = request.data.get("address")
        website = request.data.get("website", "")
        contact_number = request.data.get("contact_number", "")

        # ✅ Accept both category_id and legacy category (for backward compat)
        category_id = request.data.get("category_id") or request.data.get(
            "category"
        )

        is_recommended = (
            request.data.get("is_recommended", "false").lower() == "true"
        )
        logo = request.FILES.get("logo")
        longitude = request.data.get("longitude") or None
        latitude = request.data.get("latitude") or None

        # ── Basic validation ─────────────────
        if not name:
            return Response(
                {"success": False, "message": "Name is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not address:
            return Response(
                {"success": False, "message": "Address is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── Category resolve ─────────────────
        category = None
        if category_id:
            try:
                category = CollegeCategory.objects.get(pk=category_id)
            except (CollegeCategory.DoesNotExist, ValueError, TypeError):
                return Response(
                    {
                        "success": False,
                        "message": f"Category with id {category_id} not found",
                        "errors": {"category_id": ["Invalid category id"]},
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # ── Create college ───────────────────
        college = College.objects.create(
            name=name,
            address=address,
            website=website,
            contact_number=contact_number,
            category=category,
            is_recommended=is_recommended,
            longitude=longitude,
            latitude=latitude,
        )

        if logo:
            college.logo = logo
            college.save()

        # ── Multiple images ──────────────────
        images = request.FILES.getlist("images")
        for image in images:
            CollegeImage.objects.create(college=college, image=image)

        serializer = CollegeSerializer(college, context={"user_id": None})
        return Response(
            {
                "success": True,
                "message": "College created successfully",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


# ═════════════════════════════════════════════
#  LIST
# ═════════════════════════════════════════════
class CollegeListView(APIView):
    def get(self, request):
        category_id = request.query_params.get("category_id")
        is_recommended = request.query_params.get("is_recommended")
        search = request.query_params.get("search")
        user_id = request.query_params.get("user_id")

        colleges = College.objects.select_related("category").all().order_by(
            "-id"
        )

        if category_id:
            colleges = colleges.filter(category_id=category_id)

        if is_recommended is not None:
            is_rec_bool = is_recommended.lower() == "true"
            colleges = colleges.filter(is_recommended=is_rec_bool)

        if search:
            colleges = colleges.filter(
                models.Q(name__icontains=search)
                | models.Q(address__icontains=search)
            )

        serializer = CollegeSerializer(
            colleges, many=True, context={"user_id": user_id}
        )
        return Response(
            {
                "success": True,
                "count": colleges.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ═════════════════════════════════════════════
#  LIST BY USER
# ═════════════════════════════════════════════
class CollegeListByUserView(APIView):
    def get(self, request, user_id):
        category_id = request.query_params.get("category_id")
        search = request.query_params.get("search")

        colleges = College.objects.select_related("category").all().order_by(
            "-id"
        )

        if category_id:
            colleges = colleges.filter(category_id=category_id)

        if search:
            colleges = colleges.filter(
                models.Q(name__icontains=search)
                | models.Q(address__icontains=search)
            )

        serializer = CollegeSerializer(
            colleges, many=True, context={"user_id": user_id}
        )
        return Response(
            {
                "success": True,
                "user_id": str(user_id),
                "count": colleges.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ═════════════════════════════════════════════
#  DETAIL / UPDATE / DELETE
# ═════════════════════════════════════════════
class CollegeDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, pk):
        try:
            return College.objects.select_related("category").get(pk=pk)
        except College.DoesNotExist:
            return None

    def get(self, request, pk):
        college = self.get_object(pk)
        if not college:
            return Response(
                {"success": False, "message": "College not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_id = request.query_params.get("user_id")
        serializer = CollegeSerializer(college, context={"user_id": user_id})
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        college = self.get_object(pk)
        if not college:
            return Response(
                {"success": False, "message": "College not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # ── Scalar fields ────────────────────
        college.name = request.data.get("name", college.name)
        college.address = request.data.get("address", college.address)
        college.website = request.data.get("website", college.website)
        college.contact_number = request.data.get(
            "contact_number", college.contact_number
        )

        # ── Category handling ────────────────
        category_id = request.data.get("category_id") or request.data.get(
            "category"
        )

        if category_id is not None:
            if category_id == "" or category_id == 0:
                college.category = None  # allow clearing
            else:
                try:
                    college.category = CollegeCategory.objects.get(
                        pk=category_id
                    )
                except (CollegeCategory.DoesNotExist, ValueError, TypeError):
                    return Response(
                        {
                            "success": False,
                            "message": f"Category with id {category_id} not found",
                            "errors": {"category_id": ["Invalid category id"]},
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        if request.data.get("is_recommended") is not None:
            college.is_recommended = (
                request.data.get("is_recommended", "false").lower() == "true"
            )
        if request.data.get("longitude") is not None:
            college.longitude = request.data.get("longitude")
        if request.data.get("latitude") is not None:
            college.latitude = request.data.get("latitude")

        logo = request.FILES.get("logo")
        if logo:
            college.logo = logo

        college.save()

        # ── Replace images ───────────────────
        images = request.FILES.getlist("images")
        if images:
            college.images.all().delete()
            for image in images:
                CollegeImage.objects.create(college=college, image=image)

        serializer = CollegeSerializer(college, context={"user_id": None})
        return Response(
            {
                "success": True,
                "message": "College updated successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        college = self.get_object(pk)
        if not college:
            return Response(
                {"success": False, "message": "College not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        college.delete()
        return Response(
            {"success": True, "message": "College deleted successfully"},
            status=status.HTTP_200_OK,
        )