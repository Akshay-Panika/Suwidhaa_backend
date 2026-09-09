from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Tiffin, TiffinImage
from .serializers import TiffinSerializer


class TiffinCreateView(APIView):
    """Create a new tiffin"""

    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser
    ]

    def post(self, request):

        user_id = request.data.get('user_id')
        title = request.data.get('title')
        description = request.data.get('description')
        price = request.data.get('price')

        is_veg = request.data.get('is_veg', '')
        is_nonveg = request.data.get('is_nonveg', '')
        is_booking = request.data.get('is_booking', False)
        rating = request.data.get('rating', 0)

        contact_number = request.data.get('contact_number', '')
        near_college = request.data.get('near_college', '')

        # Convert boolean
        if isinstance(is_booking, str):
            is_booking = is_booking.lower() == 'true'

        # Validate user_id
        if not user_id:
            return Response({
                "success": False,
                "message": "user_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate title
        if not title:
            return Response({
                "success": False,
                "message": "Title is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate description
        if not description:
            return Response({
                "success": False,
                "message": "Description is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate price
        if not price:
            return Response({
                "success": False,
                "message": "Price is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create Tiffin
        tiffin = Tiffin.objects.create(
            user_id=user_id,
            title=title,
            description=description,
            price=price,
            is_veg=is_veg,
            is_nonveg=is_nonveg,
            is_booking=is_booking,
            rating=rating,
            contact_number=contact_number,
            near_college=near_college
        )

        # Handle images
        images = request.FILES.getlist('images')

        for image in images:
            TiffinImage.objects.create(
                tiffin=tiffin,
                image=image
            )

        serializer = TiffinSerializer(tiffin)

        return Response({
            "success": True,
            "message": "Tiffin created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


class TiffinListView(APIView):
    """List all tiffins with filters"""

    def get(self, request):

        user_id = request.query_params.get('user_id')
        is_veg = request.query_params.get('is_veg')
        is_nonveg = request.query_params.get('is_nonveg')
        is_booking = request.query_params.get('is_booking')
        near_college = request.query_params.get('near_college')
        search = request.query_params.get('search')

        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')

        min_rating = request.query_params.get('min_rating')
        max_rating = request.query_params.get('max_rating')

        # All tiffins
        tiffins = Tiffin.objects.all()

        # User ID filter
        if user_id:
            tiffins = tiffins.filter(user_id=user_id)

        # Veg filter
        if is_veg is not None:
            tiffins = tiffins.filter(
                is_veg__icontains=is_veg
            )

        # Non Veg filter
        if is_nonveg is not None:
            tiffins = tiffins.filter(
                is_nonveg__icontains=is_nonveg
            )

        # Booking filter
        if is_booking is not None:

            is_booking_bool = (
                is_booking.lower() == 'true'
            )

            tiffins = tiffins.filter(
                is_booking=is_booking_bool
            )

        # Near college filter
        if near_college:
            tiffins = tiffins.filter(
                near_college__icontains=near_college
            )

        # Search
        if search:
            tiffins = tiffins.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        # Price filters
        if min_price:
            tiffins = tiffins.filter(
                price__gte=min_price
            )

        if max_price:
            tiffins = tiffins.filter(
                price__lte=max_price
            )

        # Rating filters
        if min_rating:
            tiffins = tiffins.filter(
                rating__gte=min_rating
            )

        if max_rating:
            tiffins = tiffins.filter(
                rating__lte=max_rating
            )

        serializer = TiffinSerializer(
            tiffins,
            many=True
        )

        return Response({
            "success": True,
            "count": tiffins.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class TiffinDetailView(APIView):
    """Get, update, delete a specific tiffin"""

    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser
    ]

    def get_object(self, pk):

        try:
            return Tiffin.objects.get(pk=pk)

        except Tiffin.DoesNotExist:
            return None

    def get(self, request, pk):

        tiffin = self.get_object(pk)

        if not tiffin:
            return Response({
                "success": False,
                "message": "Tiffin not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = TiffinSerializer(tiffin)

        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, pk):

        tiffin = self.get_object(pk)

        if not tiffin:
            return Response({
                "success": False,
                "message": "Tiffin not found"
            }, status=status.HTTP_404_NOT_FOUND)

        # Update user_id
        tiffin.user_id = request.data.get(
            'user_id',
            tiffin.user_id
        )

        # Update fields
        tiffin.title = request.data.get(
            'title',
            tiffin.title
        )

        tiffin.description = request.data.get(
            'description',
            tiffin.description
        )

        tiffin.price = request.data.get(
            'price',
            tiffin.price
        )

        tiffin.is_veg = request.data.get(
            'is_veg',
            tiffin.is_veg
        )

        tiffin.is_nonveg = request.data.get(
            'is_nonveg',
            tiffin.is_nonveg
        )

        tiffin.near_college = request.data.get(
            'near_college',
            tiffin.near_college
        )

        tiffin.contact_number = request.data.get(
            'contact_number',
            tiffin.contact_number
        )

        # Booking
        is_booking = request.data.get(
            'is_booking',
            tiffin.is_booking
        )

        if isinstance(is_booking, str):
            is_booking = is_booking.lower() == 'true'

        tiffin.is_booking = is_booking

        # Rating
        rating = request.data.get(
            'rating',
            tiffin.rating
        )

        if rating:
            tiffin.rating = rating

        tiffin.save()

        # Handle images
        images = request.FILES.getlist('images')

        if images:

            tiffin.tiffin_images.all().delete()

            for image in images:
                TiffinImage.objects.create(
                    tiffin=tiffin,
                    image=image
                )

        serializer = TiffinSerializer(tiffin)

        return Response({
            "success": True,
            "message": "Tiffin updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def delete(self, request, pk):

        tiffin = self.get_object(pk)

        if not tiffin:
            return Response({
                "success": False,
                "message": "Tiffin not found"
            }, status=status.HTTP_404_NOT_FOUND)

        tiffin.delete()

        return Response({
            "success": True,
            "message": "Tiffin deleted successfully"
        }, status=status.HTTP_200_OK)