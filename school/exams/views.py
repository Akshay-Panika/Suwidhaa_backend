from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from school.school_type.models import SchoolType
from .models import ClassExamTimetable
from .serializers import ClassExamTimetableSerializer


class ClassExamTimetableCreateView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, school_id):
        school = get_object_or_404(SchoolType, pk=school_id)
        
        data = request.data.copy()
        data['school'] = school.id
        
        serializer = ClassExamTimetableSerializer(
            data=data, context={'request': request}
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


class ClassExamTimetableListView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, school_id):
        school = get_object_or_404(SchoolType, pk=school_id)
        qs = ClassExamTimetable.objects.filter(school=school).prefetch_related('schedules__invigilator')

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


class ClassExamTimetableDetailView(APIView):
    authentication_classes = []
    permission_classes = []

    def _get_object(self, school_id, pk):
        return get_object_or_404(ClassExamTimetable, pk=pk, school_id=school_id)

    def get(self, request, school_id, pk):
        obj = self._get_object(school_id, pk)
        serializer = ClassExamTimetableSerializer(
            obj, context={'request': request}
        )
        return Response(
            {'success': True, 'data': serializer.data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, school_id, pk):
        obj = self._get_object(school_id, pk)
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

    def patch(self, request, school_id, pk):
        obj = self._get_object(school_id, pk)
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

    def delete(self, request, school_id, pk):
        obj = self._get_object(school_id, pk)
        obj.delete()
        return Response(
            {'success': True, 'message': 'Timetable deleted successfully.'},
            status=status.HTTP_200_OK,
        )