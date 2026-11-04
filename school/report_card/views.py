from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import ReportCard
from .serializers import ReportCardSerializer, ReportCardCreateSerializer
from django.db import transaction

# ---------------------------------------------------------
class ReportCardBulkCreateView(APIView):
    def post(self, request):
        teacher_id = request.data.get('teacher_id')
        class_name = request.data.get('class_name')
        subject_name = request.data.get('subject_name')
        exam_name = request.data.get('exam_name')
        total_marks = request.data.get('sujectmaks_marks')
        passing_marks = request.data.get('pasingmaks_marks')
        students = request.data.get('students', [])

        # ── validate common fields once ──
        common_errors = {}
        if not teacher_id:
            common_errors['teacher_id'] = 'Required'
        if not class_name:
            common_errors['class_name'] = 'Required'
        if not subject_name:
            common_errors['subject_name'] = 'Required'
        if not exam_name:
            common_errors['exam_name'] = 'Required'
        if total_marks in (None, ''):
            common_errors['sujectmaks_marks'] = 'Required'
        if passing_marks in (None, ''):
            common_errors['pasingmaks_marks'] = 'Required'
        if not isinstance(students, list) or not students:
            common_errors['students'] = 'Select at least one student'

        if common_errors:
            return Response(
                {'status': False, 'message': 'Validation error',
                 'errors': common_errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created, failures = [], []

        # per-student validation & save
        with transaction.atomic():
            for i, s in enumerate(students):
                if not isinstance(s, dict):
                    failures.append({
                        'index': i, 'student_id': None,
                        'errors': 'Invalid student entry'
                    })
                    continue

                payload = {
                    'teacher_id': str(teacher_id).strip(),
                    'student_id': str(s.get('student_id', '')).strip(),
                    'class_name': class_name,
                    'subject_name': subject_name,
                    'exam_name': exam_name,
                    'sujectmaks_marks': total_marks,
                    'pasingmaks_marks': passing_marks,
                    'student_marks': s.get('student_marks'),
                    'result': s.get('result') or (
                        'pass'
                        if int(s.get('student_marks') or 0) >= int(passing_marks)
                        else 'fail'
                    ),
                    'description': s.get('description', '') or '',
                }

                ser = ReportCardCreateSerializer(data=payload)
                if ser.is_valid():
                    rc = ser.save()
                    created.append(ReportCardSerializer(rc).data)
                else:
                    failures.append({
                        'index': i,
                        'student_id': payload['student_id'],
                        'errors': ser.errors,
                    })

        return Response(
            {
                'status': True,
                'message': f'{len(created)} created, {len(failures)} failed',
                'created_count': len(created),
                'failed_count': len(failures),
                'created': created,
                'failures': failures,
            },
            status=status.HTTP_201_CREATED
            if created else status.HTTP_400_BAD_REQUEST,
        )
    
# ---------------------------------------------------------
# CREATE  ->  POST /report-cards/create/
# Returns full teacher + student model in response
# ---------------------------------------------------------
class ReportCardCreateView(APIView):
    def post(self, request):
        serializer = ReportCardCreateSerializer(data=request.data)
        if serializer.is_valid():
            rc = serializer.save()
            return Response(
                {
                    'status': True,
                    'message': 'Report card created successfully',
                    'data': ReportCardSerializer(rc).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                'status': False,
                'message': 'Validation error',
                'errors': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ---------------------------------------------------------
# LIST  ->  GET /report-cards/list/
# ---------------------------------------------------------
class ReportCardListView(APIView):
    def get(self, request):
        qs = ReportCard.objects.all().order_by('-created_at')

        # Optional filters
        teacher_id = request.GET.get('teacher_id')
        student_id = request.GET.get('student_id')
        class_name = request.GET.get('class_name')

        if teacher_id:
            qs = qs.filter(teacher_id=str(teacher_id).strip())
        if student_id:
            qs = qs.filter(student_id=str(student_id).strip())
        if class_name:
            qs = qs.filter(class_name__iexact=str(class_name).strip())

        serializer = ReportCardSerializer(qs, many=True)
        return Response(
            {
                'status': True,
                'message': 'Report cards fetched successfully',
                'count': qs.count(),
                'data': serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------
# DETAIL  ->  GET / PUT / PATCH / DELETE /report-cards/list/<id>/
# ---------------------------------------------------------
class ReportCardDetailView(APIView):
    def get_object(self, pk):
        return get_object_or_404(ReportCard, pk=pk)

    def get(self, request, pk):
        rc = self.get_object(pk)
        return Response(
            {
                'status': True,
                'message': 'Report card fetched successfully',
                'data': ReportCardSerializer(rc).data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        rc = self.get_object(pk)
        serializer = ReportCardCreateSerializer(rc, data=request.data)
        if serializer.is_valid():
            rc = serializer.save()
            return Response(
                {
                    'status': True,
                    'message': 'Report card updated successfully',
                    'data': ReportCardSerializer(rc).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                'status': False,
                'message': 'Validation error',
                'errors': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        rc = self.get_object(pk)
        serializer = ReportCardCreateSerializer(
            rc, data=request.data, partial=True
        )
        if serializer.is_valid():
            rc = serializer.save()
            return Response(
                {
                    'status': True,
                    'message': 'Report card partially updated successfully',
                    'data': ReportCardSerializer(rc).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                'status': False,
                'message': 'Validation error',
                'errors': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        rc = self.get_object(pk)
        rc.delete()
        return Response(
            {
                'status': True,
                'message': 'Report card deleted successfully',
            },
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------
# STUDENT WISE LIST  ->  GET /report-cards/student-list/<student_id>/
# <student_id> = Student DB integer id (as string)
# ---------------------------------------------------------
class ReportCardByStudentIdView(APIView):
    def get(self, request, student_id):
        target = str(student_id).strip()

        # Validate integer id
        try:
            int(target)
        except (ValueError, TypeError):
            return Response(
                {
                    'status': False,
                    'message': f"Invalid student_id '{student_id}' — must be a DB integer id",
                    'data': [],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = ReportCard.objects.filter(student_id=target).order_by('-created_at')

        if not qs.exists():
            return Response(
                {
                    'status': False,
                    'message': f'No report cards found for student_id: {student_id}',
                    'count': 0,
                    'data': [],
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ReportCardSerializer(qs, many=True)
        return Response(
            {
                'status': True,
                'message': f'Report cards fetched for student_id: {student_id}',
                'count': qs.count(),
                'data': serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------
# TEACHER WISE LIST  ->  GET /report-cards/teacher/<teacher_id>/
# <teacher_id> = teacher_id_card
# ---------------------------------------------------------
class ReportCardByTeacherView(APIView):
    def get(self, request, teacher_id):
        target = str(teacher_id).strip()
        qs = ReportCard.objects.filter(teacher_id=target).order_by('-created_at')

        if not qs.exists():
            return Response(
                {
                    'status': False,
                    'message': f'No report cards found for teacher_id: {teacher_id}',
                    'count': 0,
                    'data': [],
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ReportCardSerializer(qs, many=True)
        return Response(
            {
                'status': True,
                'message': f'Report cards fetched for teacher_id: {teacher_id}',
                'count': qs.count(),
                'data': serializer.data,
            },
            status=status.HTTP_200_OK,
        )