from django.db import models
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Room, RoomImage
from .serializers import RoomSerializer
from college.colleges.models import College
from college.colleges.serializers import CollegeSerializer


# ═════════════════════════════════════════════
#  CREATE ROOM (College-wise)
# ═════════════════════════════════════════════
class RoomCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        college_id = request.data.get("college_id") or request.data.get(
            "college"
        )
        room_number = request.data.get("room_number")
        room_type = request.data.get("room_type", "")
        capacity = request.data.get("capacity", 1)
        rent_or_fee = request.data.get("rent_or_fee") or None
        is_available = (
            request.data.get("is_available", "true").lower() == "true"
        )
        description = request.data.get("description", "")

        # ── Basic validation ─────────────────
        if not college_id:
            return Response(
                {"success": False, "message": "college_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not room_number:
            return Response(
                {"success": False, "message": "Room number is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── College resolve ──────────────────
        try:
            college = College.objects.select_related("category").get(
                pk=college_id
            )
        except (College.DoesNotExist, ValueError, TypeError):
            return Response(
                {
                    "success": False,
                    "message": f"College with id {college_id} not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # ── Create Room ──────────────────────
        room = Room.objects.create(
            college=college,
            room_number=room_number,
            room_type=room_type,
            capacity=capacity,
            rent_or_fee=rent_or_fee,
            is_available=is_available,
            description=description,
        )

        # ── Multiple images ──────────────────
        images = request.FILES.getlist("images")
        for image in images:
            RoomImage.objects.create(room=room, image=image)

        serializer = RoomSerializer(room)
        return Response(
            {
                "success": True,
                "message": "Room created successfully",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


# ═════════════════════════════════════════════
#  LIST ROOMS BY COLLEGE (WITH COLLEGE MODEL)
# ═════════════════════════════════════════════
class CollegeRoomListView(APIView):
    def get(self, request, college_id):
        try:
            college = College.objects.select_related("category").get(pk=college_id)
        except (College.DoesNotExist, ValueError, TypeError):
            return Response(
                {"success": False, "message": "College not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        is_available = request.query_params.get("is_available")
        search = request.query_params.get("search")
        user_id = request.query_params.get("user_id")

        rooms = Room.objects.filter(college=college).order_by("-id")

        if is_available is not None:
            is_avail_bool = is_available.lower() == "true"
            rooms = rooms.filter(is_available=is_avail_bool)

        if search:
            rooms = rooms.filter(
                models.Q(room_number__icontains=search)
                | models.Q(room_type__icontains=search)
            )

        college_data = CollegeSerializer(
            college, context={"user_id": user_id}
        ).data
        room_serializer = RoomSerializer(rooms, many=True)

        return Response(
            {
                "success": True,
                "college_id": college.id,
                "college": college_data,
                "count": rooms.count(),
                "data": room_serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ═════════════════════════════════════════════
#  DETAIL / UPDATE / DELETE ROOM
# ═════════════════════════════════════════════
class RoomDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, pk):
        try:
            return Room.objects.select_related(
                "college", "college__category"
            ).get(pk=pk)
        except Room.DoesNotExist:
            return None

    def get(self, request, pk):
        room = self.get_object(pk)
        if not room:
            return Response(
                {"success": False, "message": "Room not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = RoomSerializer(room)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        room = self.get_object(pk)
        if not room:
            return Response(
                {"success": False, "message": "Room not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        college_id = request.data.get("college_id") or request.data.get(
            "college"
        )
        if college_id:
            try:
                room.college = College.objects.select_related("category").get(
                    pk=college_id
                )
            except (College.DoesNotExist, ValueError, TypeError):
                return Response(
                    {
                        "success": False,
                        "message": f"College with id {college_id} not found",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        room.room_number = request.data.get("room_number", room.room_number)
        room.room_type = request.data.get("room_type", room.room_type)
        room.capacity = request.data.get("capacity", room.capacity)
        room.description = request.data.get("description", room.description)

        if request.data.get("rent_or_fee") is not None:
            room.rent_or_fee = request.data.get("rent_or_fee") or None

        if request.data.get("is_available") is not None:
            room.is_available = (
                request.data.get("is_available", "true").lower() == "true"
            )

        room.save()

        images = request.FILES.getlist("images")
        if images:
            room.images.all().delete()
            for image in images:
                RoomImage.objects.create(room=room, image=image)

        serializer = RoomSerializer(room)
        return Response(
            {
                "success": True,
                "message": "Room updated successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        room = self.get_object(pk)
        if not room:
            return Response(
                {"success": False, "message": "Room not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        room.delete()
        return Response(
            {"success": True, "message": "Room deleted successfully"},
            status=status.HTTP_200_OK,
        )