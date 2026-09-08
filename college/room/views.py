from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from django.db import IntegrityError
import logging
from .models import Room, RoomImage
from .serializers import RoomSerializer

logger = logging.getLogger(__name__)

class RoomCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        try:
            # Debug logging
            logger.info(f"Request data: {request.data}")
            logger.info(f"Request FILES: {request.FILES}")
            
            # Get user_id - TRY MULTIPLE SOURCES
            user_id = request.data.get('user_id')
            
            # If not in data, check if it's in POST body as string
            if not user_id and hasattr(request, 'POST'):
                user_id = request.POST.get('user_id')
            
            # If still not found, check query params
            if not user_id:
                user_id = request.query_params.get('user_id')
            
            # Log what we found
            logger.info(f"User ID extracted: {user_id}")
            
            # VALIDATE USER_ID FIRST
            if not user_id:
                return Response({
                    "success": False,
                    "message": "User ID is required. Please provide user_id in the request."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Convert user_id to string and ensure it's not too long
            user_id = str(user_id)[:10]  # Max length 10
            
            # Get other data
            title = request.data.get('title')
            description = request.data.get('description')
            address = request.data.get('address')
            price = request.data.get('price')
            room_type = request.data.get('room_type', '')
            is_booking = request.data.get('is_booking', False)
            contact_number = request.data.get('contact_number', '')
            wifi = request.data.get('wifi', False)
            ac = request.data.get('ac', False)
            parking = request.data.get('parking', False)
            security = request.data.get('security', False)
            laundry = request.data.get('laundry', False)
            water = request.data.get('water', False)
            near_college = request.data.get('near_college', '')
            
            # Convert boolean strings to actual booleans
            boolean_fields = {
                'is_booking': is_booking,
                'wifi': wifi,
                'ac': ac,
                'parking': parking,
                'security': security,
                'laundry': laundry,
                'water': water
            }
            
            for field, value in boolean_fields.items():
                if isinstance(value, str):
                    boolean_fields[field] = value.lower() == 'true'
                elif isinstance(value, bool):
                    boolean_fields[field] = value
                else:
                    boolean_fields[field] = False
            
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
            
            # Create room
            room = Room.objects.create(
                user_id=user_id,
                title=title,
                description=description,
                address=address,
                price=price,
                room_type=room_type,
                is_booking=boolean_fields['is_booking'],
                contact_number=contact_number,
                wifi=boolean_fields['wifi'],
                ac=boolean_fields['ac'],
                parking=boolean_fields['parking'],
                security=boolean_fields['security'],
                laundry=boolean_fields['laundry'],
                water=boolean_fields['water'],
                near_college=near_college
            )
            
            logger.info(f"Room created with ID: {room.id}, User ID: {room.user_id}")
            
            # Handle images
            images = request.FILES.getlist('images')
            for image in images:
                RoomImage.objects.create(
                    room=room,
                    image=image
                )
            
            # Return response
            serializer = RoomSerializer(room)
            return Response({
                "success": True,
                "message": "Room created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except IntegrityError as e:
            logger.error(f"IntegrityError: {str(e)}")
            return Response({
                "success": False,
                "message": f"Database error: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error creating room: {str(e)}")
            return Response({
                "success": False,
                "message": f"Error creating room: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RoomListView(APIView):
    def get(self, request):
        try:
            # Get category filter from query params
            user_id = request.query_params.get('user_id')
            room_type = request.query_params.get('room_type')
            is_booking = request.query_params.get('is_booking')
            near_college = request.query_params.get('near_college')
            search = request.query_params.get('search')
            min_price = request.query_params.get('min_price')
            max_price = request.query_params.get('max_price')
            wifi = request.query_params.get('wifi')
            ac = request.query_params.get('ac')
            parking = request.query_params.get('parking')
            
            # Start with all rooms
            rooms = Room.objects.all()
            
            # Apply filters
            if user_id:
                rooms = rooms.filter(user_id=user_id)
            
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
            logger.error(f"Error in RoomListView: {str(e)}")
            return Response({
                "success": False,
                "message": f"Error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RoomDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    
    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            return None
    
    def get(self, request, pk):
        try:
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
            
        except Exception as e:
            logger.error(f"Error in RoomDetailView GET: {str(e)}")
            return Response({
                "success": False,
                "message": f"Error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request, pk):
        try:
            room = self.get_object(pk)
            if not room:
                return Response({
                    "success": False,
                    "message": "Room not found"
                }, status=status.HTTP_404_NOT_FOUND)
            
            logger.info(f"PUT Request data: {request.data}")
            
            # Get user_id - try multiple sources
            user_id = request.data.get('user_id')
            if not user_id:
                user_id = request.POST.get('user_id')
            
            if user_id:
                room.user_id = str(user_id)[:10]
            
            # Update fields
            room.title = request.data.get('title', room.title)
            room.description = request.data.get('description', room.description)
            room.address = request.data.get('address', room.address)
            
            price = request.data.get('price')
            if price:
                room.price = price
            
            room.room_type = request.data.get('room_type', room.room_type)
            room.contact_number = request.data.get('contact_number', room.contact_number)
            
            # Update boolean fields
            boolean_fields = ['is_booking', 'wifi', 'ac', 'parking', 'security', 'laundry', 'water']
            for field in boolean_fields:
                value = request.data.get(field)
                if value is not None:
                    if isinstance(value, str):
                        value = value.lower() == 'true'
                    elif not isinstance(value, bool):
                        value = False
                    setattr(room, field, value)
            
            room.near_college = request.data.get('near_college', room.near_college)
            
            room.save()
            logger.info(f"Room updated: {room.id}, User ID: {room.user_id}")
            
            # Handle images
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
            logger.error(f"Error in RoomDetailView PUT: {str(e)}")
            return Response({
                "success": False,
                "message": f"Error updating room: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, pk):
        try:
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
            
        except Exception as e:
            logger.error(f"Error in RoomDetailView DELETE: {str(e)}")
            return Response({
                "success": False,
                "message": f"Error deleting room: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)