from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from datetime import datetime, date

from .models import StudentAttendance
from .serializers import BulkAttendanceSerializer
from school.student.models import Student
from school.student.serializers import StudentSerializer


def _student_info(student):
    return StudentSerializer(student).data


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


class StudentAttendanceCreateView(APIView):
    def post(self, request):
        serializer = BulkAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = []
        errors = []

        with transaction.atomic():
            for idx, item in enumerate(serializer.validated_data['students']):
                student_id = item['student_id']

                try:
                    student = Student.objects.select_related('school').get(pk=student_id)
                except Student.DoesNotExist:
                    errors.append({
                        "index": idx,
                        "student_id": student_id,
                        "error": f"Student with id '{student_id}' not found."
                    })
                    continue

                att, _ = StudentAttendance.objects.update_or_create(
                    student=student,
                    date=item['date'],
                    defaults={
                        'attendance_status': item.get('attendance_status', 'present'),
                        'remarks': item.get('remarks') or '',
                    }
                )

                result.append({
                    "student": _student_info(student),
                    "attendance": {
                        "id": att.id,
                        "date": att.date.strftime('%Y-%m-%d'),
                        "day_name": att.date.strftime('%A'),
                        "attendance_status": att.attendance_status,
                        "remarks": att.remarks or '',
                        "created_at": att.created_at,
                        "updated_at": att.updated_at,
                    }
                })

        if result and not errors:
            return Response(
                {
                    "status": True,
                    "message": "Attendance saved successfully.",
                    "total": len(result),
                    "data": result,
                },
                status=status.HTTP_200_OK
            )

        if result and errors:
            return Response(
                {
                    "status": True,
                    "message": "Partial success. Some records were saved and some failed.",
                    "saved_count": len(result),
                    "failed_count": len(errors),
                    "data": result,
                    "errors": errors,
                },
                status=status.HTTP_207_MULTI_STATUS
            )

        return Response(
            {
                "status": False,
                "message": "No records were saved.",
                "errors": errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class StudentAttendanceListView(APIView):
    def get(self, request):
        student_qs = Student.objects.select_related('school').all()

        student_id = request.query_params.get('student_id')
        card_id = request.query_params.get('student_id_card')
        cls = request.query_params.get('class')
        school_id = request.query_params.get('school_id')

        if student_id:
            student_qs = student_qs.filter(id=student_id)
        if card_id:
            student_qs = student_qs.filter(student_id_card__icontains=card_id)
        if cls:
            student_qs = student_qs.filter(student_class__icontains=cls)
        if school_id:
            student_qs = student_qs.filter(school_id=school_id)

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
                "student": _student_info(student),
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


class StudentAttendanceDetailView(APIView):
    def get(self, request, student_id):
        try:
            student = Student.objects.select_related('school').get(pk=student_id)
        except Student.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "error": f"Student with id '{student_id}' not found."
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
                "student": _student_info(student),
                "total_records": att_qs.count(),
                "history": build_history(att_qs),
            },
            status=status.HTTP_200_OK
        )


class StudentAttendanceDeleteView(APIView):
    def delete(self, request, student_id, date):
        try:
            student = Student.objects.select_related('school').get(pk=student_id)
        except Student.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "error": f"Student with id '{student_id}' not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {
                    "status": False,
                    "error": f"Invalid date format '{date}'. Use YYYY-MM-DD."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            att = StudentAttendance.objects.get(student=student, date=date_obj)
        except StudentAttendance.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "error": f"No attendance found for student id '{student_id}' on {date}."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        deleted_attendance = {
            "id": att.id,
            "date": att.date.strftime('%Y-%m-%d'),
            "attendance_status": att.attendance_status,
            "remarks": att.remarks or '',
        }

        att.delete()

        return Response(
            {
                "status": True,
                "message": "Attendance deleted successfully.",
                "deleted": {
                    "student": _student_info(student),
                    "attendance": deleted_attendance,
                },
            },
            status=status.HTTP_200_OK
        )


class StudentAttendanceTodayView(APIView):
    def get(self, request, student_id):
        # 1. Fetch the student
        try:
            student = Student.objects.select_related('school').get(pk=student_id)
        except Student.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "error": f"Student with id '{student_id}' not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        today = date.today()

        # 2. Try to fetch today's attendance
        try:
            att = StudentAttendance.objects.get(student=student, date=today)
        except StudentAttendance.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": f"No attendance record found for today ({today.strftime('%Y-%m-%d')}).",
                    "student": _student_info(student),
                    "date": today.strftime('%Y-%m-%d'),
                    "day_name": today.strftime('%A'),
                    "attendance": None,
                },
                status=status.HTTP_200_OK
            )

        # 3. Return today's attendance
        return Response(
            {
                "status": True,
                "message": "Today's attendance fetched successfully.",
                "student": _student_info(student),
                "date": today.strftime('%Y-%m-%d'),
                "day_name": today.strftime('%A'),
                "attendance": {
                    "id": att.id,
                    "date": att.date.strftime('%Y-%m-%d'),
                    "day_name": att.date.strftime('%A'),
                    "month": att.date.strftime('%B'),
                    "year": att.date.year,
                    "attendance_status": att.attendance_status,
                    "remarks": att.remarks or '',
                    "created_at": att.created_at,
                    "updated_at": att.updated_at,
                },
            },
            status=status.HTTP_200_OK
        )