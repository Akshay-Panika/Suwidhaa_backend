from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q
from .models import Room, RoomImage
from .serializers import RoomSerializer, RoomCreateUpdateSerializer

class RoomCreateView(APIView):
    """Create a new room"""
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request):
        try:
            # Log everything for debugging
            print("=== REQUEST DATA ===")
            print("Data:", request.data)
            print("FILES:", request.FILES)
            print("POST:", request.POST)
            
            # Get data
            title = request.data.get('title')
            description = request.data.get('description')
            address = request.data.get('address')
            price = request.data.get('price')
            room_type = request.data.get('room_type', '')
            
            # Validate required fields
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
            
            # Get boolean fields (handle both string and boolean)
            is_booking = request.data.get('is_booking', False)
            if isinstance(is_booking, str):
                is_booking = is_booking.lower() == 'true'
            
            wifi = request.data.get('wifi', False)
            if isinstance(wifi, str):
                wifi = wifi.lower() == 'true'
            
            ac = request.data.get('ac', False)
            if isinstance(ac, str):
                ac = ac.lower() == 'true'
            
            parking = request.data.get('parking', False)
            if isinstance(parking, str):
                parking = parking.lower() == 'true'
            
            security = request.data.get('security', False)
            if isinstance(security, str):
                security = security.lower() == 'true'
            
            laundry = request.data.get('laundry', False)
            if isinstance(laundry, str):
                laundry = laundry.lower() == 'true'
            
            water = request.data.get('water', False)
            if isinstance(water, str):
                water = water.lower() == 'true'
            
            near_college = request.data.get('near_college', '')
            
            # Create room
            room = Room.objects.create(
                title=title,
                description=description,
                address=address,
                price=price,
                room_type=room_type,
                is_booking=is_booking,
                wifi=wifi,
                ac=ac,
                parking=parking,
                security=security,
                laundry=laundry,
                water=water,
                near_college=near_college
            )
            
            # Handle images - IMPORTANT: use 'images' key, not 'room_images'
            images = request.FILES.getlist('images')
            print(f"Number of images: {len(images)}")
            
            for image in images:
                print(f"Processing image: {image.name}")
                RoomImage.objects.create(
                    room=room,
                    image=image
                )
            
            serializer = RoomSerializer(room)
            return Response({
                "success": True,
                "message": "Room created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({
                "success": False,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RoomListView(APIView):
    """List all rooms with filters"""
    
    def get(self, request):
        try:
            # Get query parameters
            is_booking = request.query_params.get('is_booking')
            near_college = request.query_params.get('near_college')
            search = request.query_params.get('search')
            min_price = request.query_params.get('min_price')
            max_price = request.query_params.get('max_price')
            wifi = request.query_params.get('wifi')
            ac = request.query_params.get('ac')
            parking = request.query_params.get('parking')
            room_type = request.query_params.get('room_type')
            
            # Start with all rooms
            rooms = Room.objects.all()
            
            # Apply filters
            if is_booking is not None:
                is_booking_bool = is_booking.lower() == 'true'
                rooms = rooms.filter(is_booking=is_booking_bool)
            
            if near_college:
                rooms = rooms.filter(near_college__icontains=near_college)
            
            if room_type:
                rooms = rooms.filter(room_type__icontains=room_type)
            
            if search:
                rooms = rooms.filter(
                    Q(title__icontains=search) |
                    Q(description__icontains=search) |
                    Q(address__icontains=search)
                )
            
            if min_price:
                rooms = rooms.filter(price__gte=min_price)
            
            if max_price:
                rooms = rooms.filter(price__lte=max_price)
            
            if wifi is not None:
                wifi_bool = wifi.lower() == 'true'
                rooms = rooms.filter(wifi=wifi_bool)
            
            if ac is not None:
                ac_bool = ac.lower() == 'true'
                rooms = rooms.filter(ac=ac_bool)
            
            if parking is not None:
                parking_bool = parking.lower() == 'true'
                rooms = rooms.filter(parking=parking_bool)
            
            serializer = RoomSerializer(rooms, many=True)
            return Response({
                "success": True,
                "count": rooms.count(),
                "data": serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "success": False,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RoomDetailView(APIView):
    """Get, update, delete a specific room"""
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            return None
    
    def get(self, request, pk):
        room = self.get_object(pk)
        if not room:
            return Response({
                "success": False,
                "message": "Room not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RoomSerializer(room)
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        room = self.get_object(pk)
        if not room:
            return Response({
                "success": False,
                "message": "Room not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Update basic fields
            room.title = request.data.get('title', room.title)
            room.description = request.data.get('description', room.description)
            room.address = request.data.get('address', room.address)
            room.price = request.data.get('price', room.price)
            room.room_type = request.data.get('room_type', room.room_type)
            
            # Update boolean fields
            is_booking = request.data.get('is_booking', room.is_booking)
            if isinstance(is_booking, str):
                is_booking = is_booking.lower() == 'true'
            room.is_booking = is_booking
            
            wifi = request.data.get('wifi', room.wifi)
            if isinstance(wifi, str):
                wifi = wifi.lower() == 'true'
            room.wifi = wifi
            
            ac = request.data.get('ac', room.ac)
            if isinstance(ac, str):
                ac = ac.lower() == 'true'
            room.ac = ac
            
            parking = request.data.get('parking', room.parking)
            if isinstance(parking, str):
                parking = parking.lower() == 'true'
            room.parking = parking
            
            security = request.data.get('security', room.security)
            if isinstance(security, str):
                security = security.lower() == 'true'
            room.security = security
            
            laundry = request.data.get('laundry', room.laundry)
            if isinstance(laundry, str):
                laundry = laundry.lower() == 'true'
            room.laundry = laundry
            
            water = request.data.get('water', room.water)
            if isinstance(water, str):
                water = water.lower() == 'true'
            room.water = water
            
            room.near_college = request.data.get('near_college', room.near_college)
            
            room.save()
            
            # Handle images if provided - IMPORTANT: use 'images' key
            images = request.FILES.getlist('images')
            if images:
                room.room_images.all().delete()
                for image in images:
                    RoomImage.objects.create(
                        room=room,
                        image=image
                    )
            
            serializer = RoomSerializer(room)
            return Response({
                "success": True,
                "message": "Room updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "success": False,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, pk):
        room = self.get_object(pk)
        if not room:
            return Response({
                "success": False,
                "message": "Room not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        room.delete()
        return Response({
            "success": True,
            "message": "Room deleted successfully"
        }, status=status.HTTP_200_OK)