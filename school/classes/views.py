from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser

from .models import Class
from .serializers import ClassSerializer


class ClassCreateView(APIView):
    parser_classes = [JSONParser]
    
    def post(self, request):
        serializer = ClassSerializer(data=request.data)
        
        if serializer.is_valid():
            class_instance = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Class created successfully",
                    "data": ClassSerializer(class_instance).data,
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


class ClassListView(APIView):
    def get(self, request):
        classes = Class.objects.all().order_by('-id')
        serializer = ClassSerializer(classes, many=True)
        
        return Response(
            {
                "success": True,
                "count": classes.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ClassDetailView(APIView):
    parser_classes = [JSONParser]
    
    def get_object(self, pk):
        try:
            return Class.objects.get(pk=pk)
        except Class.DoesNotExist:
            return None
    
    def get(self, request, pk):
        class_instance = self.get_object(pk)
        
        if not class_instance:
            return Response(
                {
                    "success": False,
                    "message": "Class not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        
        return Response(
            {
                "success": True,
                "data": ClassSerializer(class_instance).data,
            },
            status=status.HTTP_200_OK,
        )
    
    def put(self, request, pk):
        class_instance = self.get_object(pk)
        
        if not class_instance:
            return Response(
                {
                    "success": False,
                    "message": "Class not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        
        serializer = ClassSerializer(class_instance, data=request.data)
        
        if serializer.is_valid():
            class_instance = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Class updated successfully",
                    "data": ClassSerializer(class_instance).data,
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
        class_instance = self.get_object(pk)
        
        if not class_instance:
            return Response(
                {
                    "success": False,
                    "message": "Class not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        
        serializer = ClassSerializer(class_instance, data=request.data, partial=True)
        
        if serializer.is_valid():
            class_instance = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Class updated successfully",
                    "data": ClassSerializer(class_instance).data,
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
        class_instance = self.get_object(pk)
        
        if not class_instance:
            return Response(
                {
                    "success": False,
                    "message": "Class not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        
        class_instance.delete()
        
        return Response(
            {
                "success": True,
                "message": "Class deleted successfully",
            },
            status=status.HTTP_200_OK,
        )