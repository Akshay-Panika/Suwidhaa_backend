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
            # update existing record
            existing.booking = booking
            existing.save()
            booking_obj = existing
        else:
            # create new record
            booking_obj = CollegeBooking.objects.create(
                college_id=college_id,
                user_id=str(user_id),
                booking=booking
            )

        # ✅ Update college-level booking flag:
        #    true if ANY user has booking=True for this college
        college.booking = CollegeBooking.objects.filter(
            college_id=college_id,
            booking=True
        ).exists()
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

        # ✅ Recalculate college-level booking flag after delete
        try:
            college = College.objects.get(pk=college_id)
            college.booking = CollegeBooking.objects.filter(
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