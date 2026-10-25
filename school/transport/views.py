from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db import models
import logging

from .models import Transport, TransportStudent
from .serializers import (
    TransportSerializer,
    TransportStudentSerializer
)
from school.student.models import Student

logger = logging.getLogger(__name__)


class TransportCreateView(APIView):
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
    """Get ALL transports (No filter)"""
    def get(self, request):
        queryset = Transport.objects.all()
        
        # Optional search by vehicle or driver
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(vehicle_number__icontains=search) |
                models.Q(driver_name__icontains=search)
            )
        
        queryset = queryset.prefetch_related('assigned_students__student')
        serializer = TransportSerializer(queryset, many=True)
        
        return Response({
            "success": True,
            "count": queryset.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)


# ✅ NEW: School wise Transport View
class TransportBySchoolView(APIView):
    """Get Transport by School ID"""
    def get(self, request, school_id):
        transports = Transport.objects.filter(school_id=school_id).prefetch_related('assigned_students__student')
        
        if not transports.exists():
            return Response(
                {
                    "success": False,
                    "message": f"No transports found for school id '{school_id}'",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
            
        serializer = TransportSerializer(transports, many=True)
        return Response(
            {
                "success": True,
                "school_id": school_id,
                "count": transports.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class TransportDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_object(self, pk):
        try:
            return Transport.objects.get(pk=pk)
        except Transport.DoesNotExist:
            return None
    
    def get(self, request, pk):
        transport = self.get_object(pk)
        if not transport:
            return Response({"success": False, "message": "Transport not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"success": True, "data": TransportSerializer(transport).data}, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        transport = self.get_object(pk)
        if not transport:
            return Response({"success": False, "message": "Transport not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TransportSerializer(transport, data=request.data)
        if serializer.is_valid():
            transport = serializer.save()
            return Response({"success": True, "message": "Updated successfully", "data": TransportSerializer(transport).data}, status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        transport = self.get_object(pk)
        if not transport:
            return Response({"success": False, "message": "Transport not found"}, status=status.HTTP_404_NOT_FOUND)
        transport.delete()
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)


class TransportStudentAddView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request, pk):
        try:
            transport = Transport.objects.get(pk=pk)
        except Transport.DoesNotExist:
            return Response({"success": False, "message": "Transport not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TransportStudentSerializer(data=request.data)
        if serializer.is_valid():
            student_instance = serializer.validated_data['student']
            
            if TransportStudent.objects.filter(transport=transport, student=student_instance).exists():
                return Response({
                    "success": False, 
                    "message": "Student is already assigned to this transport"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save(transport=transport)
            return Response({
                "success": True,
                "message": "Student added successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
            
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class TransportStudentDeleteView(APIView):
    def delete(self, request, pk, student_id):
        try:
            transport = Transport.objects.get(pk=pk)
        except Transport.DoesNotExist:
            return Response({"success": False, "message": "Transport not found"}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            student_assign = TransportStudent.objects.get(transport=transport, student_id=student_id)
            student_assign.delete()
            return Response({"success": True, "message": "Student removed successfully"}, status=status.HTTP_200_OK)
        except TransportStudent.DoesNotExist:
            return Response({"success": False, "message": "Student not found in this transport"}, status=status.HTTP_404_NOT_FOUND)