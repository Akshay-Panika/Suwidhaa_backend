from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from datetime import datetime

from .models import Student, StudentAttendance
from .serializers import BulkAttendanceSerializer


# =========================================================
#  HELPER — History grouping (year -> month -> days[])
# =========================================================
def build_history(attendance_qs):
    history = {}

    for att in attendance_qs:
        year = str(att.date.year)
        month_name = att.date.strftime('%B')
        day_name = att.date.strftime('%A')

        history.setdefault(year, {})
        history[year].setdefault(month_name, [])

        history[year][month_name].append({
            "id": att.id,
            "date": att.date.strftime('%Y-%m-%d'),
            "day_name": day_name,
            "month": month_name,
            "year": att.date.year,
            "attendance_status": att.attendance_status,
            "remarks": att.remarks or '',
            "created_at": att.created_at,
            "updated_at": att.updated_at,
        })

    return history


# =========================================================
#  CREATE / UPDATE  — Bulk (1 ya N) — date-wise
# =========================================================
class StudentAttendanceCreateView(APIView):
    """
    POST /api/v1/school/student-attendance/create/

    Body:
    {
        "students": [
            {
                "student_card_id": "A004",
                "student_name": "Ram Kumar",
                "student_class": "5A",
                "school_type": "Primary",
                "date": "2026-09-24",
                "attendance_status": "present",
                "remarks": "on time"
            }
        ]
    }

    - (student_card_id + date) exist karta hai → UPDATE
    - Nahi hai → CREATE
    - Student master bhi create/update hota hai
    """

    def post(self, request):
        serializer = BulkAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = []

        with transaction.atomic():
            for item in serializer.validated_data['students']:
                card_id = item['student_card_id']

                # ---- 1. Student master create/update ----
                student, _ = Student.objects.update_or_create(
                    student_card_id=card_id,
                    defaults={
                        'student_name': item.get('student_name') or '',
                        'student_class': item.get('student_class') or '',
                        'school_type': item.get('school_type') or '',
                    }
                )

                # ---- 2. Attendance create/update (date-wise) ----
                att, is_created = StudentAttendance.objects.update_or_create(
                    student=student,
                    date=item['date'],
                    defaults={
                        'attendance_status': item.get('attendance_status', 'present'),
                        'remarks': item.get('remarks') or '',
                    }
                )

                result.append({
                    "id": att.id,
                    "student_card_id": student.student_card_id,
                    "student_name": student.student_name,
                    "student_class": student.student_class,
                    "school_type": student.school_type,
                    "date": att.date.strftime('%Y-%m-%d'),
                    "day_name": att.date.strftime('%A'),
                    "attendance_status": att.attendance_status,
                    "remarks": att.remarks or '',
                    "created_at": att.created_at,
                    "updated_at": att.updated_at,
                })

        return Response(
            {
                "status": True,
                "message": "Attendance saved successfully",
                "total": len(result),
                "data": result,
            },
            status=status.HTTP_200_OK
        )


# =========================================================
#  LIST ALL STUDENTS (year -> month -> days)
# =========================================================
class StudentAttendanceListView(APIView):
    """
    GET /api/v1/school/student-attendance/list/
    Optional filters:
        ?student_card_id=A004
        ?class=5A
        ?school_type=Primary
        ?year=2026
        ?month=September
        ?attendance_status=present
    """

    def get(self, request):
        student_qs = Student.objects.all()

        card_id = request.query_params.get('student_card_id')
        cls = request.query_params.get('class')
        school_type = request.query_params.get('school_type')

        if card_id:
            student_qs = student_qs.filter(student_card_id__icontains=card_id)
        if cls:
            student_qs = student_qs.filter(student_class__icontains=cls)
        if school_type:
            student_qs = student_qs.filter(school_type__icontains=school_type)

        year_filter = request.query_params.get('year')
        month_filter = request.query_params.get('month')
        status_filter = request.query_params.get('attendance_status')

        result = []

        for student in student_qs:
            att_qs = student.attendances.all()

            if year_filter:
                att_qs = att_qs.filter(date__year=year_filter)
            if month_filter:
                try:
                    month_num = datetime.strptime(month_filter, '%B').month
                    att_qs = att_qs.filter(date__month=month_num)
                except ValueError:
                    pass
            if status_filter:
                att_qs = att_qs.filter(attendance_status=status_filter)

            att_qs = att_qs.order_by('-date')

            result.append({
                "student_card_id": student.student_card_id,
                "student_name": student.student_name,
                "student_class": student.student_class,
                "school_type": student.school_type,
                "total_records": att_qs.count(),
                "history": build_history(att_qs),
            })

        return Response(
            {
                "status": True,
                "total_students": len(result),
                "students": result,
            },
            status=status.HTTP_200_OK
        )


# =========================================================
#  SINGLE STUDENT — full history
# =========================================================
class StudentAttendanceDetailView(APIView):
    """
    GET /api/v1/school/student-attendance/list/<student_card_id>/
    Optional:
        ?year=2026
        ?month=September
        ?attendance_status=present
    """

    def get(self, request, student_card_id):
        try:
            student = Student.objects.get(student_card_id=student_card_id)
        except Student.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "error": f"Student with card_id '{student_card_id}' not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        att_qs = student.attendances.all()

        year_filter = request.query_params.get('year')
        month_filter = request.query_params.get('month')
        status_filter = request.query_params.get('attendance_status')

        if year_filter:
            att_qs = att_qs.filter(date__year=year_filter)
        if month_filter:
            try:
                month_num = datetime.strptime(month_filter, '%B').month
                att_qs = att_qs.filter(date__month=month_num)
            except ValueError:
                pass
        if status_filter:
            att_qs = att_qs.filter(attendance_status=status_filter)

        att_qs = att_qs.order_by('-date')

        return Response(
            {
                "status": True,
                "student_card_id": student.student_card_id,
                "student_name": student.student_name,
                "student_class": student.student_class,
                "school_type": student.school_type,
                "total_records": att_qs.count(),
                "history": build_history(att_qs),
            },
            status=status.HTTP_200_OK
        )