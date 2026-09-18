# college/college_booking/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CollegeBooking
from .serializers import CollegeBookingSerializer
from college.colleges.models import College
from services.whatsapp_service import WhatsAppService


# ============================================================
# CollegeBookingCreateView (Aapka existing — NO CHANGE)
# URL: POST /api/v1/college/college-booking/create/
# ============================================================
class CollegeBookingCreateView(APIView):
    def post(self, request):
        college_id = request.data.get('college_id')
        user_id = request.data.get('user_id')
        booking = request.data.get('booking', 'true')
        message = request.data.get('message', '')

        # ✅ Nested room object
        room = request.data.get('room', {}) or {}
        room_id = room.get('room_id') if room else None
        room_name = room.get('room_name') if room else None
        room_type = room.get('room_type') if room else None
        room_amount = room.get('room_amount') if room else None

        # ✅ Nested tiffin object
        tiffin = request.data.get('tiffin', {}) or {}
        tiffin_id = tiffin.get('tiffin_id') if tiffin else None
        tiffin_name = tiffin.get('tiffin_name') if tiffin else None
        tiffin_type = tiffin.get('tiffin_type') if tiffin else None
        tiffin_amount = tiffin.get('tiffin_amount') if tiffin else None

        # Convert booking to boolean
        if isinstance(booking, str):
            booking = booking.lower() == 'true'
        else:
            booking = bool(booking)

        # Validate
        if not college_id:
            return Response({"success": False, "message": "college_id is required"},
                            status=status.HTTP_400_BAD_REQUEST)
        if not user_id:
            return Response({"success": False, "message": "user_id is required"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if college exists
        try:
            college = College.objects.get(pk=college_id)
        except College.DoesNotExist:
            return Response({"success": False, "message": "College not found"},
                            status=status.HTTP_404_NOT_FOUND)

        # ✅ FIX: Determine booking type based on what's provided
        is_room_booking = room_id is not None
        is_tiffin_booking = tiffin_id is not None
        is_college_only = not is_room_booking and not is_tiffin_booking

        # ✅ FIX: Build filter for existing record
        if is_room_booking:
            existing = CollegeBooking.objects.filter(
                college_id=college_id,
                user_id=str(user_id),
                room_id=room_id,
                booking=True,
            ).first()
        elif is_tiffin_booking:
            existing = CollegeBooking.objects.filter(
                college_id=college_id,
                user_id=str(user_id),
                tiffin_id=tiffin_id,
                booking=True,
            ).first()
        else:
            existing = CollegeBooking.objects.filter(
                college_id=college_id,
                user_id=str(user_id),
                room_id__isnull=True,
                tiffin_id__isnull=True,
                booking=True,
            ).first()

        if existing:
            # ✅ Update existing record
            existing.booking = booking
            existing.message = message

            if is_room_booking:
                existing.room_id = room_id
                existing.room_name = room_name
                existing.room_type = room_type
                existing.room_amount = room_amount

            if is_tiffin_booking:
                existing.tiffin_id = tiffin_id
                existing.tiffin_name = tiffin_name
                existing.tiffin_type = tiffin_type
                existing.tiffin_amount = tiffin_amount

            existing.save()
            booking_obj = existing
        else:
            # ✅ Naya record — jo bheja wahi save karo
            booking_obj = CollegeBooking.objects.create(
                college_id=college_id,
                user_id=str(user_id),
                booking=booking,
                message=message,
                room_id=room_id,
                room_name=room_name,
                room_type=room_type,
                room_amount=room_amount,
                tiffin_id=tiffin_id,
                tiffin_name=tiffin_name,
                tiffin_type=tiffin_type,
                tiffin_amount=tiffin_amount,
            )

        # ✅ Update college-level booking flag
        college.is_booked = CollegeBooking.objects.filter(
            college_id=college_id,
            booking=True
        ).exists()
        college.save()

        # WhatsApp
        whatsapp_result = None
        if booking and message and college.contact_number:
            try:
                wa_service = WhatsAppService()
                whatsapp_result = wa_service.send_custom_message(
                    phone_number=college.contact_number,
                    message_body=message
                )
            except Exception as e:
                whatsapp_result = {"success": False, "error": str(e)}

        serializer = CollegeBookingSerializer(booking_obj)
        return Response({
            "success": True,
            "message": "College booked successfully",
            "data": serializer.data,
            "whatsapp": whatsapp_result
        }, status=status.HTTP_201_CREATED)


# ============================================================
# ✅ NAYA — CollegeBookingListView
# URL: GET /api/v1/college/college-booking/list/
# Query params: ?user_id=1, ?college_id=1
# ============================================================
class CollegeBookingListView(APIView):
    """
    GET /api/v1/college/college-booking/list/

    Query params (optional):
    - user_id: filter bookings by user
    - college_id: filter bookings by college

    Returns list of all college bookings with nested room + tiffin.
    """

    def get(self, request):
        college_id = request.query_params.get('college_id')
        user_id = request.query_params.get('user_id')

        bookings = CollegeBooking.objects.all().order_by('-id')

        # ✅ Filter by college_id
        if college_id:
            bookings = bookings.filter(college_id=college_id)

        # ✅ Filter by user_id
        if user_id:
            bookings = bookings.filter(user_id=str(user_id))

        serializer = CollegeBookingSerializer(bookings, many=True)

        return Response({
            "success": True,
            "count": bookings.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)


# ============================================================
# ✅ NAYA — CollegeBookingDetailView
# URL: GET/DELETE /api/v1/college/college-booking/<pk>/
# ============================================================
class CollegeBookingDetailView(APIView):
    """
    GET    /api/v1/college/college-booking/<pk>/ → get single booking
    DELETE /api/v1/college/college-booking/<pk>/ → delete booking
    """

    def get_object(self, pk):
        try:
            return CollegeBooking.objects.get(pk=pk)
        except CollegeBooking.DoesNotExist:
            return None

    def get(self, request, pk):
        booking = self.get_object(pk)

        if not booking:
            return Response({
                "success": False,
                "message": "Booking not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CollegeBookingSerializer(booking)

        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        booking = self.get_object(pk)

        if not booking:
            return Response({
                "success": False,
                "message": "Booking not found"
            }, status=status.HTTP_404_NOT_FOUND)

        college_id = booking.college_id
        booking.delete()

        # ✅ Recalculate college-level booking flag
        try:
            college = College.objects.get(pk=college_id)
            college.is_booked = CollegeBooking.objects.filter(
                college_id=college_id,
                booking=True
            ).exists()
            college.save()
        except College.DoesNotExist:
            pass

        return Response({
            "success": True,
            "message": "Booking deleted successfully"
        }, status=status.HTTP_200_OK)