# school/exams/views.py
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import ClassExamTimetable
from .serializers import ClassExamTimetableSerializer


# ==================== CREATE ====================
class ClassExamTimetableCreateView(APIView):
    """
    POST /api/v1/school/exam-timetables/create/
    Body may contain:
      - created_by_id   (int, optional)
      - created_by_name (string, optional)
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = ClassExamTimetableSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            timetable = serializer.save()
            return Response(
                {
                    'success': True,
                    'message': 'Timetable created successfully.',
                    'data': ClassExamTimetableSerializer(
                        timetable, context={'request': request}
                    ).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {'success': False, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==================== LIST ====================
class ClassExamTimetableListView(APIView):
    """
    GET /api/v1/school/exam-timetables/list/
    Optional query: ?class_name=10th&exam_type=board
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        qs = ClassExamTimetable.objects.all().prefetch_related('schedules')

        class_name = request.query_params.get('class_name')
        exam_type = request.query_params.get('exam_type')

        if class_name:
            qs = qs.filter(class_name=class_name)
        if exam_type:
            qs = qs.filter(exam_type=exam_type)

        serializer = ClassExamTimetableSerializer(
            qs, many=True, context={'request': request}
        )
        return Response(
            {'success': True, 'count': qs.count(), 'data': serializer.data},
            status=status.HTTP_200_OK,
        )


# ==================== DETAIL ====================
class ClassExamTimetableDetailView(APIView):
    authentication_classes = []
    permission_classes = []

    def _get_object(self, pk):
        return get_object_or_404(ClassExamTimetable, pk=pk)

    def get(self, request, pk):
        obj = self._get_object(pk)
        serializer = ClassExamTimetableSerializer(
            obj, context={'request': request}
        )
        return Response(
            {'success': True, 'data': serializer.data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        obj = self._get_object(pk)
        serializer = ClassExamTimetableSerializer(
            obj, data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            timetable = serializer.save()
            return Response(
                {
                    'success': True,
                    'message': 'Timetable updated successfully.',
                    'data': ClassExamTimetableSerializer(
                        timetable, context={'request': request}
                    ).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {'success': False, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        obj = self._get_object(pk)
        serializer = ClassExamTimetableSerializer(
            obj, data=request.data, partial=True,
            context={'request': request},
        )
        if serializer.is_valid():
            timetable = serializer.save()
            return Response(
                {
                    'success': True,
                    'message': 'Timetable updated successfully.',
                    'data': ClassExamTimetableSerializer(
                        timetable, context={'request': request}
                    ).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {'success': False, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        obj = self._get_object(pk)
        obj.delete()
        return Response(
            {'success': True, 'message': 'Timetable deleted successfully.'},
            status=status.HTTP_200_OK,
        )