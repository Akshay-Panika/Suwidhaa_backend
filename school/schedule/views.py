from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Schedule
from .serializers import ScheduleSerializer


class ScheduleCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request):
        serializer = ScheduleSerializer(data=request.data)
        
        if serializer.is_valid():
            schedule_instance = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Schedule created successfully",
                    "data": ScheduleSerializer(schedule_instance).data,
                },
                status=status.HTTP_201_CREATED,
            )
        
        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class ScheduleListView(APIView):
    def get(self, request):
        schedules = Schedule.objects.all().order_by('-id')
        serializer = ScheduleSerializer(schedules, many=True)
        
        return Response(
            {
                "success": True,
                "count": schedules.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ScheduleDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_object(self, pk):
        try:
            return Schedule.objects.get(pk=pk)
        except Schedule.DoesNotExist:
            return None
    
    def get(self, request, pk):
        schedule_instance = self.get_object(pk)
        
        if not schedule_instance:
            return Response(
                {
                    "success": False,
                    "message": "Schedule not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        
        return Response(
            {
                "success": True,
                "data": ScheduleSerializer(schedule_instance).data,
            },
            status=status.HTTP_200_OK,
        )
    
    def put(self, request, pk):
        schedule_instance = self.get_object(pk)
        
        if not schedule_instance:
            return Response(
                {
                    "success": False,
                    "message": "Schedule not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        
        serializer = ScheduleSerializer(schedule_instance, data=request.data)
        
        if serializer.is_valid():
            schedule_instance = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Schedule updated successfully",
                    "data": ScheduleSerializer(schedule_instance).data,
                },
                status=status.HTTP_200_OK,
            )
        
        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    def patch(self, request, pk):
        schedule_instance = self.get_object(pk)
        
        if not schedule_instance:
            return Response(
                {
                    "success": False,
                    "message": "Schedule not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        
        serializer = ScheduleSerializer(schedule_instance, data=request.data, partial=True)
        
        if serializer.is_valid():
            schedule_instance = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Schedule updated successfully",
                    "data": ScheduleSerializer(schedule_instance).data,
                },
                status=status.HTTP_200_OK,
            )
        
        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    def delete(self, request, pk):
        schedule_instance = self.get_object(pk)
        
        if not schedule_instance:
            return Response(
                {
                    "success": False,
                    "message": "Schedule not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        
        schedule_instance.delete()
        
        return Response(
            {
                "success": True,
                "message": "Schedule deleted successfully",
            },
            status=status.HTTP_200_OK,
        )