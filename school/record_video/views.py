from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import SchoolClass, Subject, RecordVideo
from .serializers import SchoolClassSerializer, SubjectSerializer, RecordVideoSerializer

class ClassListView(APIView):
    """
    GET /api/school/record-videos/classes/
    Returns list of classes with total video counts.
    """
    def get(self, request):
        try:
            classes = SchoolClass.objects.all()
            serializer = SchoolClassSerializer(classes, many=True)
            return Response(
                {"status": True, "count": classes.count(), "data": serializer.data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"status": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubjectListView(APIView):
    """
    GET /api/school/record-videos/subjects/
    Returns list of subjects for filter chips.
    """
    def get(self, request):
        try:
            subjects = Subject.objects.all()
            serializer = SubjectSerializer(subjects, many=True)
            return Response(
                {"status": True, "data": serializer.data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"status": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RecordVideoListView(APIView):
    """
    GET /api/school/record-videos/classes/<class_id>/videos/
    GET /api/school/record-videos/classes/<class_id>/videos/?subject_id=2
    Returns videos for a class, optionally filtered by subject.
    """
    def get(self, request, class_id):
        try:
            school_class = get_object_or_404(SchoolClass, id=class_id)
            videos = RecordVideo.objects.filter(school_class=school_class)
            
            # Filter by Subject if provided (ignore if 'all')
            subject_id = request.query_params.get('subject_id')
            if subject_id and subject_id.lower() != 'all':
                videos = videos.filter(subject_id=subject_id)

            serializer = RecordVideoSerializer(videos, many=True)
            return Response(
                {
                    "status": True, 
                    "class_name": school_class.name,
                    "count": videos.count(),
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"status": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)