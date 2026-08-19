from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser

from .models import Subject
from .serializers import SubjectSerializer


class SubjectCreateView(APIView):
    parser_classes = [JSONParser]
    
    def post(self, request):
        serializer = SubjectSerializer(data=request.data)
        
        if serializer.is_valid():
            subject_instance = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Subject created successfully",
                    "data": SubjectSerializer(subject_instance).data,
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


class SubjectListView(APIView):
    def get(self, request):
        subjects = Subject.objects.all().order_by('-id')
        serializer = SubjectSerializer(subjects, many=True)
        
        return Response(
            {
                "success": True,
                "count": subjects.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class SubjectDetailView(APIView):
    parser_classes = [JSONParser]
    
    def get_object(self, pk):
        try:
            return Subject.objects.get(pk=pk)
        except Subject.DoesNotExist:
            return None
    
    def get(self, request, pk):
        subject_instance = self.get_object(pk)
        
        if not subject_instance:
            return Response(
                {
                    "success": False,
                    "message": "Subject not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        
        return Response(
            {
                "success": True,
                "data": SubjectSerializer(subject_instance).data,
            },
            status=status.HTTP_200_OK,
        )
    
    def put(self, request, pk):
        subject_instance = self.get_object(pk)
        
        if not subject_instance:
            return Response(
                {
                    "success": False,
                    "message": "Subject not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        
        serializer = SubjectSerializer(subject_instance, data=request.data)
        
        if serializer.is_valid():
            subject_instance = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Subject updated successfully",
                    "data": SubjectSerializer(subject_instance).data,
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
        subject_instance = self.get_object(pk)
        
        if not subject_instance:
            return Response(
                {
                    "success": False,
                    "message": "Subject not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        
        serializer = SubjectSerializer(subject_instance, data=request.data, partial=True)
        
        if serializer.is_valid():
            subject_instance = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Subject updated successfully",
                    "data": SubjectSerializer(subject_instance).data,
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
        subject_instance = self.get_object(pk)
        
        if not subject_instance:
            return Response(
                {
                    "success": False,
                    "message": "Subject not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        
        subject_instance.delete()
        
        return Response(
            {
                "success": True,
                "message": "Subject deleted successfully",
            },
            status=status.HTTP_200_OK,
        )