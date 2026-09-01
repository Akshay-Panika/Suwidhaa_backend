# school/transport/views.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db import models
import logging

from .models import Transport, TransportStudent
from .serializers import (
    TransportSerializer, 
    TransportListSerializer, 
    TransportDetailSerializer,
    TransportStudentSerializer
)

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
                    "data": TransportDetailSerializer(transport).data
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
    """List all transports with full student data"""
    
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
        
        # Prefetch students for performance
        queryset = queryset.prefetch_related('students')
        
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
        
        serializer = TransportDetailSerializer(transport)
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
                    "data": TransportDetailSerializer(transport).data
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
                    "data": TransportDetailSerializer(transport).data
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


# ==================== STUDENT MANAGEMENT VIEWS ====================

class TransportStudentAddView(APIView):
    """Add a student to transport"""
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request, pk):
        try:
            transport = Transport.objects.get(pk=pk)
        except Transport.DoesNotExist:
            return Response({
                "success": False,
                "message": "Transport not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Validate required fields
        student_name = request.data.get('student_name')
        student_id = request.data.get('student_id')
        
        if not student_name or not student_id:
            return Response({
                "success": False,
                "message": "student_name and student_id are required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check for duplicate
        if TransportStudent.objects.filter(transport=transport, student_id=student_id).exists():
            return Response({
                "success": False,
                "message": f"Student with ID '{student_id}' already exists in this transport"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create student
        student = TransportStudent.objects.create(
            transport=transport,
            student_name=student_name,
            student_id=student_id,
            pickup_time=request.data.get('pickup_time'),
            drop_time=request.data.get('drop_time')
        )
        
        serializer = TransportStudentSerializer(student)
        return Response({
            "success": True,
            "message": "Student added successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


class TransportStudentBulkAddView(APIView):
    """Bulk add students to transport"""
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request, pk):
        try:
            transport = Transport.objects.get(pk=pk)
        except Transport.DoesNotExist:
            return Response({
                "success": False,
                "message": "Transport not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        students_data = request.data.get('students', [])
        
        if not students_data or not isinstance(students_data, list):
            return Response({
                "success": False,
                "message": "students list is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        created = []
        errors = []
        
        for student_data in students_data:
            student_name = student_data.get('student_name')
            student_id = student_data.get('student_id')
            
            if not student_name or not student_id:
                errors.append(f"Missing student_name or student_id for: {student_data}")
                continue
            
            # Check for duplicate
            if TransportStudent.objects.filter(transport=transport, student_id=student_id).exists():
                errors.append(f"Student with ID '{student_id}' already exists")
                continue
            
            # Create student
            student = TransportStudent.objects.create(
                transport=transport,
                student_name=student_name,
                student_id=student_id,
                pickup_time=student_data.get('pickup_time'),
                drop_time=student_data.get('drop_time')
            )
            created.append(TransportStudentSerializer(student).data)
        
        return Response({
            "success": True,
            "message": f"Added {len(created)} students successfully",
            "created": created,
            "errors": errors
        }, status=status.HTTP_201_CREATED)


class TransportStudentUpdateView(APIView):
    """Update a student in transport"""
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def put(self, request, pk, student_id):
        try:
            transport = Transport.objects.get(pk=pk)
        except Transport.DoesNotExist:
            return Response({
                "success": False,
                "message": "Transport not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            student = TransportStudent.objects.get(transport=transport, student_id=student_id)
        except TransportStudent.DoesNotExist:
            return Response({
                "success": False,
                "message": f"Student with ID '{student_id}' not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Update fields
        student.student_name = request.data.get('student_name', student.student_name)
        student.pickup_time = request.data.get('pickup_time', student.pickup_time)
        student.drop_time = request.data.get('drop_time', student.drop_time)
        student.save()
        
        serializer = TransportStudentSerializer(student)
        return Response({
            "success": True,
            "message": "Student updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def patch(self, request, pk, student_id):
        return self.put(request, pk, student_id)


class TransportStudentDeleteView(APIView):
    """Remove a student from transport"""
    
    def delete(self, request, pk, student_id):
        try:
            transport = Transport.objects.get(pk=pk)
        except Transport.DoesNotExist:
            return Response({
                "success": False,
                "message": "Transport not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            student = TransportStudent.objects.get(transport=transport, student_id=student_id)
            student.delete()
            return Response({
                "success": True,
                "message": f"Student with ID '{student_id}' removed successfully"
            }, status=status.HTTP_200_OK)
        except TransportStudent.DoesNotExist:
            return Response({
                "success": False,
                "message": f"Student with ID '{student_id}' not found"
            }, status=status.HTTP_404_NOT_FOUND)


class TransportStudentListView(APIView):
    """List all students in a transport"""
    
    def get(self, request, pk):
        try:
            transport = Transport.objects.get(pk=pk)
        except Transport.DoesNotExist:
            return Response({
                "success": False,
                "message": "Transport not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        students = transport.students.all()
        serializer = TransportStudentSerializer(students, many=True)
        
        return Response({
            "success": True,
            "count": students.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)