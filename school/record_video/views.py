from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from .models import SchoolClass, Subject, RecordVideo
from .serializers import SchoolClassSerializer, SubjectSerializer, RecordVideoSerializer

# ==================== CLASS VIEWS ====================
class ClassListCreateAPIView(APIView):
    def get(self, request):
        classes = SchoolClass.objects.all()
        return Response({"status": True, "data": SchoolClassSerializer(classes, many=True).data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = SchoolClassSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "message": "Class created", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ClassDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(SchoolClass, pk=pk)

    def put(self, request, pk):
        obj = self.get_object(pk)
        serializer = SchoolClassSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "message": "Class updated", "data": serializer.data})
        return Response({"status": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        obj.delete()
        return Response({"status": True, "message": "Class deleted"}, status=status.HTTP_204_NO_CONTENT)

# ==================== SUBJECT VIEWS ====================
class SubjectListCreateAPIView(APIView):
    def get(self, request):
        subjects = Subject.objects.all()
        return Response({"status": True, "data": SubjectSerializer(subjects, many=True).data})

    def post(self, request):
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class SubjectDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Subject, pk=pk)

    def put(self, request, pk):
        obj = self.get_object(pk)
        serializer = SubjectSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "data": serializer.data})
        return Response({"status": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        obj.delete()
        return Response({"status": True, "message": "Subject deleted"}, status=status.HTTP_204_NO_CONTENT)

# ==================== RECORD VIDEO VIEWS ====================
class RecordVideoListCreateAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, class_id):
        school_class = get_object_or_404(SchoolClass, id=class_id)
        videos = RecordVideo.objects.filter(school_class=school_class)
        
        subject_id = request.query_params.get('subject_id')
        if subject_id and subject_id.lower() != 'all':
            videos = videos.filter(subject_id=subject_id)

        return Response({"status": True, "data": RecordVideoSerializer(videos, many=True).data})

    def post(self, request, class_id):
        school_class = get_object_or_404(SchoolClass, id=class_id)
        data = request.data.copy()
        data['school_class'] = school_class.id

        serializer = RecordVideoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "message": "Video created", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class RecordVideoDetailAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, class_id, pk):
        return get_object_or_404(RecordVideo, pk=pk, school_class_id=class_id)

    def put(self, request, class_id, pk):
        obj = self.get_object(class_id, pk)
        serializer = RecordVideoSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "data": serializer.data})
        return Response({"status": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, class_id, pk):
        obj = self.get_object(class_id, pk)
        obj.delete()
        return Response({"status": True, "message": "Video deleted"}, status=status.HTTP_204_NO_CONTENT)