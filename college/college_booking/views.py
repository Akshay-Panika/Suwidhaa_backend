# college/college_booking/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CollegeBooking
from .serializers import CollegeBookingSerializer
from college.colleges.models import College
from services.whatsapp_service import WhatsAppService   # ✅ SAHI

class CollegeBookingCreateView(APIView):
    def post(self, request):
        college_id = request.data.get('college_id')
        user_id = request.data.get('user_id')
        booking = request.data.get('booking', 'true')
        message = request.data.get('message', '')   # ✅ NEW

        # ✅ ADDED: nested room object
        room = request.data.get('room', {}) or {}
        room_id = room.get('room_id')
        room_name = room.get('room_name')
        room_type = room.get('room_type')
        room_amount = room.get('room_amount')

        # ✅ ADDED: nested tiffin object
        tiffin = request.data.get('tiffin', {}) or {}
        tiffin_id = tiffin.get('tiffin_id')
        tiffin_name = tiffin.get('tiffin_name')
        tiffin_type = tiffin.get('tiffin_type')
        tiffin_amount = tiffin.get('tiffin_amount')

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

        # Check if this user has already booked this college
        existing = CollegeBooking.objects.filter(
            college_id=college_id,
            user_id=str(user_id)
        ).first()

        if existing:
            existing.booking = booking
            existing.message = message   # ✅ update message
            # ✅ ADDED: update room fields (only if provided)
            if room_id is not None:
                existing.room_id = room_id
            if room_name is not None:
                existing.room_name = room_name
            if room_type is not None:
                existing.room_type = room_type
            if room_amount is not None:
                existing.room_amount = room_amount
            # ✅ ADDED: update tiffin fields (only if provided)
            if tiffin_id is not None:
                existing.tiffin_id = tiffin_id
            if tiffin_name is not None:
                existing.tiffin_name = tiffin_name
            if tiffin_type is not None:
                existing.tiffin_type = tiffin_type
            if tiffin_amount is not None:
                existing.tiffin_amount = tiffin_amount
            existing.save()
            booking_obj = existing
        else:
            booking_obj = CollegeBooking.objects.create(
                college_id=college_id,
                user_id=str(user_id),
                booking=booking,
                message=message,   # ✅ save message
                # ✅ ADDED: room fields
                room_id=room_id,
                room_name=room_name,
                room_type=room_type,
                room_amount=room_amount,
                # ✅ ADDED: tiffin fields
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

        # ✅ WhatsApp pe message bhejo (agar message hai aur booking true hai)
        whatsapp_result = None
        if booking and message and college.contact_number:
            try:
                wa_service = WhatsAppService()
                whatsapp_result = wa_service.send_custom_message(
                    phone_number=college.contact_number,
                    message_body=message
                )
            except Exception as e:
                # WhatsApp fail ho gaya to booking fail nahi karni
                whatsapp_result = {
                    "success": False,
                    "error": str(e)
                }

        serializer = CollegeBookingSerializer(booking_obj)
        return Response({
            "success": True,
            "message": "College booked successfully",
            "data": serializer.data,
            "whatsapp": whatsapp_result   # ✅ WhatsApp result bhi bhejo
        }, status=status.HTTP_201_CREATED)


class CollegeBookingListView(APIView):
    def get(self, request):
        college_id = request.query_params.get('college_id')
        user_id = request.query_params.get('user_id')

        bookings = CollegeBooking.objects.all().order_by('-id')

        if college_id:
            bookings = bookings.filter(college_id=college_id)
        if user_id:
            bookings = bookings.filter(user_id=user_id)

        serializer = CollegeBookingSerializer(bookings, many=True)
        return Response({
            "success": True,
            "count": bookings.count(),
            "data": serializer.data   # ✅ room + tiffin automatically aayenge
        }, status=status.HTTP_200_OK)


class CollegeBookingDetailView(APIView):
    def get_object(self, pk):
        try:
            return CollegeBooking.objects.get(pk=pk)
        except CollegeBooking.DoesNotExist:
            return None

    def get(self, request, pk):
        booking = self.get_object(pk)
        if not booking:
            return Response({"success": False, "message": "Booking not found"},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = CollegeBookingSerializer(booking)
        return Response({"success": True, "data": serializer.data},
                        status=status.HTTP_200_OK)

    def delete(self, request, pk):
        booking = self.get_object(pk)
        if not booking:
            return Response({"success": False, "message": "Booking not found"},
                            status=status.HTTP_404_NOT_FOUND)

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