from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q
import cloudinary.uploader
import logging
from .models import Room, RoomImage
from .serializers import RoomSerializer

logger = logging.getLogger(__name__)

class RoomCreateView(APIView):
    """Create a new room"""
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request):
        try:
            # Log everything for debugging
            print("=== REQUEST DATA ===")
            print("Content Type:", request.content_type)
            print("Data:", request.data)
            print("FILES:", request.FILES)
            print("POST:", request.POST)
            print("FILES keys:", request.FILES.keys())
            
            # Get data from request.data (for JSON) or request.POST (for form-data)
            if request.content_type and 'application/json' in request.content_type:
                # JSON request
                title = request.data.get('title')
                description = request.data.get('description')
                address = request.data.get('address')
                price = request.data.get('price')
                room_type = request.data.get('room_type', '')
                is_booking = request.data.get('is_booking', False)
                wifi = request.data.get('wifi', False)
                ac = request.data.get('ac', False)
                parking = request.data.get('parking', False)
                security = request.data.get('security', False)
                laundry = request.data.get('laundry', False)
                water = request.data.get('water', False)
                near_college = request.data.get('near_college', '')
            else:
                # Form-data request
                title = request.POST.get('title')
                description = request.POST.get('description')
                address = request.POST.get('address')
                price = request.POST.get('price')
                room_type = request.POST.get('room_type', '')
                is_booking = request.POST.get('is_booking', 'false')
                wifi = request.POST.get('wifi', 'false')
                ac = request.POST.get('ac', 'false')
                parking = request.POST.get('parking', 'false')
                security = request.POST.get('security', 'false')
                laundry = request.POST.get('laundry', 'false')
                water = request.POST.get('water', 'false')
                near_college = request.POST.get('near_college', '')
            
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
            
            # Convert boolean values
            if isinstance(is_booking, str):
                is_booking = is_booking.lower() == 'true'
            if isinstance(wifi, str):
                wifi = wifi.lower() == 'true'
            if isinstance(ac, str):
                ac = ac.lower() == 'true'
            if isinstance(parking, str):
                parking = parking.lower() == 'true'
            if isinstance(security, str):
                security = security.lower() == 'true'
            if isinstance(laundry, str):
                laundry = laundry.lower() == 'true'
            if isinstance(water, str):
                water = water.lower() == 'true'
            
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
            
            print(f"Room created with ID: {room.id}")
            
            # Handle images - Method 1: Using request.FILES
            images = request.FILES.getlist('images')
            print(f"Images from getlist: {len(images)}")
            
            # Method 2: If getlist doesn't work, try iterating directly
            if not images:
                print("Trying alternative method...")
                for key in request.FILES.keys():
                    print(f"Key: {key}")
                    if key == 'images' or key.startswith('images'):
                        images = request.FILES.getlist(key)
                        print(f"Got {len(images)} images from key: {key}")
                        break
            
            # Method 3: Direct upload to Cloudinary
            if images:
                for idx, image in enumerate(images):
                    try:
                        print(f"Processing image {idx+1}: {image.name}")
                        
                        # Upload directly to Cloudinary
                        upload_result = cloudinary.uploader.upload(
                            image,
                            folder='suwidhaa/room/images'
                        )
                        print(f"Uploaded to Cloudinary: {upload_result['secure_url']}")
                        
                        # Create RoomImage with the uploaded file
                        RoomImage.objects.create(
                            room=room,
                            image=image
                        )
                        print(f"RoomImage created for image {idx+1}")
                        
                    except Exception as e:
                        print(f"Error uploading image {idx+1}: {str(e)}")
            else:
                print("No images found in request")
                # Try to get images from request.data
                if 'images' in request.data:
                    print(f"Images in request.data: {request.data['images']}")
            
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
            # Get data
            if request.content_type and 'application/json' in request.content_type:
                title = request.data.get('title')
                description = request.data.get('description')
                address = request.data.get('address')
                price = request.data.get('price')
                room_type = request.data.get('room_type')
                is_booking = request.data.get('is_booking')
                wifi = request.data.get('wifi')
                ac = request.data.get('ac')
                parking = request.data.get('parking')
                security = request.data.get('security')
                laundry = request.data.get('laundry')
                water = request.data.get('water')
                near_college = request.data.get('near_college')
            else:
                title = request.POST.get('title')
                description = request.POST.get('description')
                address = request.POST.get('address')
                price = request.POST.get('price')
                room_type = request.POST.get('room_type')
                is_booking = request.POST.get('is_booking')
                wifi = request.POST.get('wifi')
                ac = request.POST.get('ac')
                parking = request.POST.get('parking')
                security = request.POST.get('security')
                laundry = request.POST.get('laundry')
                water = request.POST.get('water')
                near_college = request.POST.get('near_college')
            
            # Update fields
            if title:
                room.title = title
            if description:
                room.description = description
            if address:
                room.address = address
            if price:
                room.price = price
            if room_type is not None:
                room.room_type = room_type
            
            # Update boolean fields
            if is_booking is not None:
                if isinstance(is_booking, str):
                    room.is_booking = is_booking.lower() == 'true'
                else:
                    room.is_booking = is_booking
            
            if wifi is not None:
                if isinstance(wifi, str):
                    room.wifi = wifi.lower() == 'true'
                else:
                    room.wifi = wifi
            
            if ac is not None:
                if isinstance(ac, str):
                    room.ac = ac.lower() == 'true'
                else:
                    room.ac = ac
            
            if parking is not None:
                if isinstance(parking, str):
                    room.parking = parking.lower() == 'true'
                else:
                    room.parking = parking
            
            if security is not None:
                if isinstance(security, str):
                    room.security = security.lower() == 'true'
                else:
                    room.security = security
            
            if laundry is not None:
                if isinstance(laundry, str):
                    room.laundry = laundry.lower() == 'true'
                else:
                    room.laundry = laundry
            
            if water is not None:
                if isinstance(water, str):
                    room.water = water.lower() == 'true'
                else:
                    room.water = water
            
            if near_college is not None:
                room.near_college = near_college
            
            room.save()
            
            # Handle images
            images = request.FILES.getlist('images')
            if not images:
                for key in request.FILES.keys():
                    if key == 'images' or key.startswith('images'):
                        images = request.FILES.getlist(key)
                        break
            
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
            print(f"Error updating room: {str(e)}")
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