# school/transport/views.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import logging

from .models import Transport
from .serializers import TransportSerializer, TransportListSerializer

logger = logging.getLogger(__name__)


class TransportCreateView(APIView):
    """Create a new transport"""
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request):
        serializer = TransportSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                transport = serializer.save()
                return Response({
                    "success": True,
                    "message": "Transport created successfully",
                    "data": TransportSerializer(transport).data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Failed to create transport: {str(e)}")
                return Response({
                    "success": False,
                    "message": f"Failed to create transport: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            "success": False,
            "message": "Validation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class TransportListView(APIView):
    """List all transports"""
    
    def get(self, request):
        queryset = Transport.objects.all()
        
        # Apply filters
        transport_type = request.query_params.get('transport_type')
        if transport_type:
            queryset = queryset.filter(transport_type__icontains=transport_type)
        
        # Search by vehicle number or driver name
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(vehicle_number__icontains=search) |
                models.Q(driver_name__icontains=search) |
                models.Q(transport_type__icontains=search)
            )
        
        # Ordering
        order_by = request.query_params.get('order_by', '-created_at')
        queryset = queryset.order_by(order_by)
        
        serializer = TransportListSerializer(queryset, many=True)
        
        return Response({
            "success": True,
            "count": queryset.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class TransportDetailView(APIView):
    """Retrieve, update or delete a transport"""
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_object(self, pk):
        try:
            return Transport.objects.get(pk=pk)
        except Transport.DoesNotExist:
            return None
    
    def get(self, request, pk):
        transport = self.get_object(pk)
        if not transport:
            return Response({
                "success": False,
                "message": "Transport not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TransportSerializer(transport)
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        transport = self.get_object(pk)
        if not transport:
            return Response({
                "success": False,
                "message": "Transport not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check for duplicate vehicle number
        if 'vehicle_number' in request.data:
            new_vehicle = request.data.get('vehicle_number')
            if Transport.objects.filter(
                vehicle_number__iexact=new_vehicle
            ).exclude(id=pk).exists():
                return Response({
                    "success": False,
                    "message": f"Vehicle number '{new_vehicle}' already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = TransportSerializer(transport, data=request.data)
        if serializer.is_valid():
            try:
                transport = serializer.save()
                return Response({
                    "success": True,
                    "message": "Transport updated successfully",
                    "data": TransportSerializer(transport).data
                }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Failed to update transport: {str(e)}")
                return Response({
                    "success": False,
                    "message": f"Failed to update transport: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        transport = self.get_object(pk)
        if not transport:
            return Response({
                "success": False,
                "message": "Transport not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TransportSerializer(
            transport, 
            data=request.data, 
            partial=True
        )
        if serializer.is_valid():
            try:
                transport = serializer.save()
                return Response({
                    "success": True,
                    "message": "Transport updated successfully",
                    "data": TransportSerializer(transport).data
                }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Failed to update transport: {str(e)}")
                return Response({
                    "success": False,
                    "message": f"Failed to update transport: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        transport = self.get_object(pk)
        if not transport:
            return Response({
                "success": False,
                "message": "Transport not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            transport.delete()
            return Response({
                "success": True,
                "message": "Transport deleted successfully"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Failed to delete transport: {str(e)}")
            return Response({
                "success": False,
                "message": f"Failed to delete transport: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)