
from django.db import models
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Room, RoomImage
from .serializers import RoomSerializer

from college.colleges.models import College


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def convert_bool(value, default=False):
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    return str(value).lower() in ['true', '1', 'yes']


def get_room_queryset():
    return (
        Room.objects
        .select_related('college')
        .prefetch_related('room_images')
        .order_by('-created_at')
    )


def serialize_room(room, user_id=None):
    return RoomSerializer(
        room,
        context={'user_id': user_id}
    ).data


# ============================================================
# ROOM CREATE
# POST /rooms/create/
# ============================================================

class RoomCreateView(APIView):

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):

        data = request.data

        user_id = data.get('user_id')
        title = data.get('title')
        description = data.get('description')
        address = data.get('address')
        price = data.get('price')
        college_id = data.get('college_id')

        if not user_id:
            return Response({
                "success": False,
                "message": "User ID is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        if not title:
            return Response({
                "success": False,
                "message": "Title is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        if not description:
            return Response({
                "success": False,
                "message": "Description is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        if not address:
            return Response({
                "success": False,
                "message": "Address is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        if not price:
            return Response({
                "success": False,
                "message": "Price is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        if not college_id:
            return Response({
                "success": False,
                "message": "College ID is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            college = College.objects.get(pk=college_id)
        except (College.DoesNotExist, ValueError, TypeError):
            return Response({
                "success": False,
                "message": "Invalid College ID"
            }, status=status.HTTP_400_BAD_REQUEST)

        longitude = data.get('longitude') or None
        latitude = data.get('latitude') or None

        if longitude is None:
            return Response({
                "success": False,
                "message": "Longitude is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        if latitude is None:
            return Response({
                "success": False,
                "message": "Latitude is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            room = Room.objects.create(
                user_id=user_id,
                title=title,
                description=description,
                address=address,
                price=price,
                longitude=longitude,
                latitude=latitude,
                room_type=data.get('room_type', ''),
                contact_number=data.get('contact_number', ''),

                is_booking=convert_bool(
                    data.get('is_booking'), False
                ),

                wifi=convert_bool(data.get('wifi'), False),
                ac=convert_bool(data.get('ac'), False),
                parking=convert_bool(data.get('parking'), False),
                security=convert_bool(data.get('security'), False),
                laundry=convert_bool(data.get('laundry'), False),
                water=convert_bool(data.get('water'), False),

                college=college,

                # Old text field maintained for compatibility
                near_college=college.name
            )

        except Exception as e:
            return Response({
                "success": False,
                "message": "Room creation failed",
                "errors": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        images = request.FILES.getlist('images')

        for image in images:
            RoomImage.objects.create(
                room=room,
                image=image
            )

        return Response({
            "success": True,
            "message": "Room created successfully",
            "data": serialize_room(room)
        }, status=status.HTTP_201_CREATED)


# ============================================================
# ROOM LIST - OWNER WISE
# GET /rooms/list/?user_id=10
# ============================================================

class RoomListView(APIView):

    def get(self, request):

        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({
                "success": False,
                "message": "User ID is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        rooms = get_room_queryset().filter(
            user_id=user_id
        )

        rooms = self.apply_filters(rooms, request)

        serializer = RoomSerializer(
            rooms,
            many=True,
            context={'user_id': user_id}
        )

        return Response({
            "success": True,
            "count": rooms.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def apply_filters(self, rooms, request):

        return apply_room_filters(rooms, request)


# ============================================================
# ROOM ALL LIST - ALL USERS
# GET /rooms/?user_id=10
# ============================================================

class RoomAllListView(APIView):

    def get(self, request):

        user_id = request.query_params.get('user_id')

        rooms = get_room_queryset()

        rooms = apply_room_filters(rooms, request)

        serializer = RoomSerializer(
            rooms,
            many=True,
            context={'user_id': user_id}
        )

        return Response({
            "success": True,
            "count": rooms.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)


# ============================================================
# ROOM LIST BY COLLEGE ID
# GET /rooms/college/5/?user_id=10
# ============================================================

class RoomListByCollegeView(APIView):

    def get(self, request, college_id):

        user_id = request.query_params.get('user_id')

        try:
            college = College.objects.get(pk=college_id)
        except College.DoesNotExist:
            return Response({
                "success": False,
                "message": "College not found"
            }, status=status.HTTP_404_NOT_FOUND)

        rooms = get_room_queryset().filter(
            college_id=college_id
        )

        rooms = apply_room_filters(rooms, request)

        serializer = RoomSerializer(
            rooms,
            many=True,
            context={'user_id': user_id}
        )

        return Response({
            "success": True,
            "message": "College rooms fetched successfully",
            "college_id": college.id,
            "college_name": college.name,
            "count": rooms.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)


# ============================================================
# COMMON FILTER FUNCTION
# ============================================================

def apply_room_filters(rooms, request):

    params = request.query_params

    room_type = params.get('room_type')
    is_booking = params.get('is_booking')
    near_college = params.get('near_college')
    search = params.get('search')

    min_price = params.get('min_price')
    max_price = params.get('max_price')

    wifi = params.get('wifi')
    ac = params.get('ac')
    parking = params.get('parking')

    if room_type:
        rooms = rooms.filter(
            room_type__icontains=room_type
        )

    if is_booking is not None:
        rooms = rooms.filter(
            is_booking=convert_bool(is_booking)
        )

    if near_college:
        rooms = rooms.filter(
            models.Q(college__name__icontains=near_college) |
            models.Q(near_college__icontains=near_college)
        )

    if search:
        rooms = rooms.filter(
            models.Q(title__icontains=search) |
            models.Q(description__icontains=search) |
            models.Q(address__icontains=search)
        )

    if min_price:
        rooms = rooms.filter(price__gte=min_price)

    if max_price:
        rooms = rooms.filter(price__lte=max_price)

    if wifi is not None:
        rooms = rooms.filter(wifi=convert_bool(wifi))

    if ac is not None:
        rooms = rooms.filter(ac=convert_bool(ac))

    if parking is not None:
        rooms = rooms.filter(parking=convert_bool(parking))

    return rooms


# ============================================================
# ROOM DETAIL / UPDATE / DELETE
# ============================================================

class RoomDetailView(APIView):

    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, pk):

        return get_object_or_404(
            get_room_queryset(),
            pk=pk
        )

    # GET DETAIL
    def get(self, request, pk):

        try:
            room = self.get_object(pk)
        except Room.DoesNotExist:
            return Response({
                "success": False,
                "message": "Room not found"
            }, status=status.HTTP_404_NOT_FOUND)

        user_id = request.query_params.get('user_id')

        return Response({
            "success": True,
            "data": serialize_room(room, user_id)
        }, status=status.HTTP_200_OK)

    # UPDATE
    def put(self, request, pk):

        try:
            room = self.get_object(pk)
        except Room.DoesNotExist:
            return Response({
                "success": False,
                "message": "Room not found"
            }, status=status.HTTP_404_NOT_FOUND)

        data = request.data

        scalar_fields = [
            'user_id',
            'title',
            'description',
            'address',
            'price',
            'room_type',
            'contact_number'
        ]

        for field in scalar_fields:
            if field in data:
                setattr(room, field, data.get(field))

        # College update
        if 'college_id' in data:

            college_id = data.get('college_id')

            if college_id == '':
                room.college = None
                room.near_college = ''

            else:
                try:
                    college = College.objects.get(pk=college_id)
                    room.college = college
                    room.near_college = college.name

                except (College.DoesNotExist, ValueError, TypeError):
                    return Response({
                        "success": False,
                        "message": "Invalid College ID"
                    }, status=status.HTTP_400_BAD_REQUEST)

        # Coordinates
        if 'longitude' in data and data.get('longitude') != '':
            room.longitude = data.get('longitude')

        if 'latitude' in data and data.get('latitude') != '':
            room.latitude = data.get('latitude')

        # Boolean fields
        boolean_fields = [
            'is_booking',
            'wifi',
            'ac',
            'parking',
            'security',
            'laundry',
            'water'
        ]

        for field in boolean_fields:
            if field in data:
                setattr(
                    room,
                    field,
                    convert_bool(data.get(field))
                )

        room.save()

        # Replace old images if new images are uploaded
        images = request.FILES.getlist('images')

        if images:
            room.room_images.all().delete()

            for image in images:
                RoomImage.objects.create(
                    room=room,
                    image=image
                )

        user_id = request.query_params.get('user_id')

        return Response({
            "success": True,
            "message": "Room updated successfully",
            "data": serialize_room(room, user_id)
        }, status=status.HTTP_200_OK)

    # DELETE
    def delete(self, request, pk):

        try:
            room = self.get_object(pk)
        except Room.DoesNotExist:
            return Response({
                "success": False,
                "message": "Room not found"
            }, status=status.HTTP_404_NOT_FOUND)

        room.delete()

        return Response({
            "success": True,
            "message": "Room deleted successfully"
        }, status=status.HTTP_200_OK)
