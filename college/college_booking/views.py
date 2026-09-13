from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CollegeBooking
from .serializers import CollegeBookingSerializer
from college.colleges.models import College   



class CollegeBookingCreateView(APIView):
    def post(self, request):
        college_id = request.data.get('college_id')
        user_id = request.data.get('user_id')
        booking = request.data.get('booking', 'true')

        # Convert booking to boolean
        if isinstance(booking, str):
            booking = booking.lower() == 'true'
        else:
            booking = bool(booking)

        # Validate
        if not college_id:
            return Response({
                "success": False,
                "message": "college_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        if not user_id:
            return Response({
                "success": False,
                "message": "user_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if college exists
        try:
            college = College.objects.get(pk=college_id)
        except College.DoesNotExist:
            return Response({
                "success": False,
                "message": "College not found"
            }, status=status.HTTP_404_NOT_FOUND)

        # Create booking record in college_booking app
        booking_obj = CollegeBooking.objects.create(
            college_id=college_id,
            user_id=str(user_id),
            booking=booking
        )

        # Sync this booking into the College model's `booking` field
        existing_bookings = college.booking or []
        if not isinstance(existing_bookings, list):
            existing_bookings = []

        # Check if this user has already booked this college
        already_booked = False
        for entry in existing_bookings:
            if isinstance(entry, dict) and str(entry.get('user_id')) == str(user_id):
                entry['booking'] = booking  # update status
                already_booked = True
                break

        # If not already booked, append new entry
        if not already_booked:
            existing_bookings.append({
                "user_id": str(user_id),
                "booking": booking
            })

        college.booking = existing_bookings
        college.save()

        serializer = CollegeBookingSerializer(booking_obj)
        return Response({
            "success": True,
            "message": "College booked successfully",
            "data": serializer.data
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
            "data": serializer.data
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

        # Also remove this entry from College.booking list
        try:
            college = College.objects.get(pk=booking.college_id)
            existing_bookings = college.booking or []
            if isinstance(existing_bookings, list):
                existing_bookings = [
                    entry for entry in existing_bookings
                    if not (isinstance(entry, dict) and str(entry.get('user_id')) == str(booking.user_id))
                ]
                college.booking = existing_bookings
                college.save()
        except College.DoesNotExist:
            pass

        booking.delete()
        return Response({
            "success": True,
            "message": "Booking deleted successfully"
        }, status=status.HTTP_200_OK)