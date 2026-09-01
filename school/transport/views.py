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
        
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
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


class TransportStudentManagementView(APIView):
    """Add, update, or remove students from transport"""
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_object(self, pk):
        try:
            return Transport.objects.get(pk=pk)
        except Transport.DoesNotExist:
            return None
    
    def post(self, request, pk):
        """Add a student to transport"""
        transport = self.get_object(pk)
        if not transport:
            return Response({
                "success": False,
                "message": "Transport not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        student_data = request.data
        
        # Validate required fields
        if not student_data.get('student_name') or not student_data.get('student_id'):
            return Response({
                "success": False,
                "message": "student_name and student_id are required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get current students list
        students = transport.students_data or []
        
        # Check for duplicate student_id
        for student in students:
            if student.get('student_id') == student_data.get('student_id'):
                return Response({
                    "success": False,
                    "message": f"Student with ID '{student_data.get('student_id')}' already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Add new student
        students.append(student_data)
        transport.students_data = students
        transport.save()
        
        return Response({
            "success": True,
            "message": "Student added successfully",
            "data": TransportSerializer(transport).data
        }, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        """Update a student in transport"""
        transport = self.get_object(pk)
        if not transport:
            return Response({
                "success": False,
                "message": "Transport not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        student_id = request.data.get('student_id')
        if not student_id:
            return Response({
                "success": False,
                "message": "student_id is required to update"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        students = transport.students_data or []
        updated = False
        
        for i, student in enumerate(students):
            if student.get('student_id') == student_id:
                # Update student data (except student_id)
                for key, value in request.data.items():
                    if key != 'student_id':
                        students[i][key] = value
                updated = True
                break
        
        if not updated:
            return Response({
                "success": False,
                "message": f"Student with ID '{student_id}' not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        transport.students_data = students
        transport.save()
        
        return Response({
            "success": True,
            "message": "Student updated successfully",
            "data": TransportSerializer(transport).data
        }, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        """Remove a student from transport"""
        transport = self.get_object(pk)
        if not transport:
            return Response({
                "success": False,
                "message": "Transport not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        student_id = request.data.get('student_id') or request.query_params.get('student_id')
        if not student_id:
            return Response({
                "success": False,
                "message": "student_id is required to delete"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        students = transport.students_data or []
        initial_count = len(students)
        
        # Remove student
        students = [s for s in students if s.get('student_id') != student_id]
        
        if len(students) == initial_count:
            return Response({
                "success": False,
                "message": f"Student with ID '{student_id}' not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        transport.students_data = students
        transport.save()
        
        return Response({
            "success": True,
            "message": "Student removed successfully",
            "data": TransportSerializer(transport).data
        }, status=status.HTTP_200_OK)