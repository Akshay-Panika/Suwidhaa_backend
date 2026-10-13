from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Booking
from .serializers import BookingSerializer, BookingCreateSerializer


class BookingCreateView(APIView):
    """
    POST /booking/create/
    Body: { user_id, service, full_name }
    """

    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Validation failed",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 🔒 Prevent duplicate active bookings (same user + same service)
        user_id = serializer.validated_data.get("user_id")
        service = serializer.validated_data.get("service")

        existing = Booking.objects.filter(
            user_id=user_id,
            service=service,
        ).exclude(status="cancelled").first()

        if existing:
            return Response(
                {
                    "success": False,
                    "message": "You have already booked this service",
                    "data": BookingSerializer(existing).data,
                },
                status=status.HTTP_409_CONFLICT,
            )

        # ✅ Create
        booking = serializer.save()

        return Response(
            {
                "success": True,
                "message": "Booking created successfully",
                "data": BookingSerializer(booking).data,
            },
            status=status.HTTP_201_CREATED,
        )


class BookingListView(APIView):
    """
    GET /booking/list/?user_id=<id>
    GET /booking/list/                (all bookings)
    Optional: ?status=pending
    """

    def get(self, request):
        bookings = Booking.objects.select_related(
            "service", "service__category"
        ).all().order_by("-id")

        user_id = request.query_params.get("user_id")
        if user_id:
            bookings = bookings.filter(user_id=user_id)

        status_filter = request.query_params.get("status")
        if status_filter:
            bookings = bookings.filter(status=status_filter)

        serializer = BookingSerializer(bookings, many=True)

        return Response(
            {
                "success": True,
                "count": bookings.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class BookingDetailView(APIView):
    """
    GET    /booking/<pk>/
    DELETE /booking/<pk>/
    PATCH  /booking/<pk>/
    """

    def get_object(self, pk):
        try:
            return Booking.objects.select_related(
                "service", "service__category"
            ).get(pk=pk)
        except Booking.DoesNotExist:
            return None

    def get(self, request, pk):
        booking = self.get_object(pk)
        if not booking:
            return Response(
                {"success": False, "message": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"success": True, "data": BookingSerializer(booking).data},
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        booking = self.get_object(pk)
        if not booking:
            return Response(
                {"success": False, "message": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = BookingSerializer(
            booking, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Booking updated successfully",
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
        booking = self.get_object(pk)
        if not booking:
            return Response(
                {"success": False, "message": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        booking.delete()
        return Response(
            {"success": True, "message": "Booking deleted successfully"},
            status=status.HTTP_200_OK,
        )