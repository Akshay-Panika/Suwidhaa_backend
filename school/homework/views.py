from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import logging

from .models import Homework
from .serializers import HomeworkSerializer

logger = logging.getLogger(__name__)


class HomeworkCreateView(APIView):
    """
    POST: Create new homework with image upload
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        # Check if required fields are present
        required_fields = ['subject_name', 'subject_topic', 'issue_date', 'end_date']
        missing_fields = [field for field in required_fields if not request.data.get(field)]
        
        if missing_fields:
            return Response({
                "success": False,
                "message": f"Required fields missing: {', '.join(missing_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = HomeworkSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                homework = serializer.save()
                return Response({
                    "success": True,
                    "message": "Homework created successfully",
                    "data": HomeworkSerializer(homework).data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Failed to create homework: {str(e)}")
                return Response({
                    "success": False,
                    "message": f"Failed to create homework: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            "success": False,
            "message": "Validation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class HomeworkListView(APIView):
    """
    GET: List all homework
    """
    def get(self, request):
        homework = Homework.objects.all().order_by("-id")
        serializer = HomeworkSerializer(homework, many=True)
        return Response({
            "success": True,
            "count": homework.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class HomeworkDetailView(APIView):
    """
    GET: Retrieve specific homework
    PUT: Update specific homework
    PATCH: Partial update specific homework
    DELETE: Delete specific homework
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return Homework.objects.get(pk=pk)
        except Homework.DoesNotExist:
            return None

    def get(self, request, pk):
        homework = self.get_object(pk)
        if not homework:
            return Response({
                "success": False,
                "message": "Homework not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            "success": True,
            "data": HomeworkSerializer(homework).data
        }, status=status.HTTP_200_OK)

    def put(self, request, pk):
        homework = self.get_object(pk)
        if not homework:
            return Response({
                "success": False,
                "message": "Homework not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = HomeworkSerializer(homework, data=request.data)
        if serializer.is_valid():
            try:
                homework = serializer.save()
                return Response({
                    "success": True,
                    "message": "Homework updated successfully",
                    "data": HomeworkSerializer(homework).data
                }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Failed to update homework: {str(e)}")
                return Response({
                    "success": False,
                    "message": f"Failed to update homework: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        homework = self.get_object(pk)
        if not homework:
            return Response({
                "success": False,
                "message": "Homework not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = HomeworkSerializer(homework, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                homework = serializer.save()
                return Response({
                    "success": True,
                    "message": "Homework updated successfully",
                    "data": HomeworkSerializer(homework).data
                }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Failed to update homework: {str(e)}")
                return Response({
                    "success": False,
                    "message": f"Failed to update homework: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        homework = self.get_object(pk)
        if not homework:
            return Response({
                "success": False,
                "message": "Homework not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            homework.delete()
            return Response({
                "success": True,
                "message": "Homework deleted successfully"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Failed to delete homework: {str(e)}")
            return Response({
                "success": False,
                "message": f"Failed to delete homework: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)