# school/teacher_attendance/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta

from .models import TeacherAttendance
from .serializers import BulkAttendanceSerializer
from school.teacher.models import Teacher
from school.teacher.serializers import TeacherSerializer


def _teacher_info(teacher):
    return TeacherSerializer(teacher).data


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
#  CREATE / UPDATE — Bulk (teacher_id based)
# =========================================================
class TeacherAttendanceCreateView(APIView):
    def post(self, request):
        serializer = BulkAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = []
        errors = []

        with transaction.atomic():
            for idx, item in enumerate(serializer.validated_data['teachers']):
                teacher_id = item['teacher_id']

                try:
                    teacher = Teacher.objects.select_related('school').get(pk=teacher_id)
                except Teacher.DoesNotExist:
                    errors.append({
                        "index": idx,
                        "teacher_id": teacher_id,
                        "error": f"Teacher with id '{teacher_id}' not found."
                    })
                    continue

                att, _ = TeacherAttendance.objects.update_or_create(
                    teacher=teacher,
                    date=item['date'],
                    defaults={
                        'attendance_status': item.get('attendance_status', 'present'),
                        'remarks': item.get('remarks') or '',
                    }
                )

                result.append({
                    "teacher": _teacher_info(teacher),
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


# =========================================================
#  LIST ALL
# =========================================================
class TeacherAttendanceListView(APIView):
    def get(self, request):
        teacher_qs = Teacher.objects.select_related('school').all()

        teacher_id = request.query_params.get('teacher_id')
        card_id = request.query_params.get('teacher_id_card')
        school_id = request.query_params.get('school_id')

        if teacher_id:
            teacher_qs = teacher_qs.filter(id=teacher_id)
        if card_id:
            teacher_qs = teacher_qs.filter(teacher_id_card__icontains=card_id)
        if school_id:
            teacher_qs = teacher_qs.filter(school_id=school_id)

        year_filter = request.query_params.get('year')
        month_filter = request.query_params.get('month')
        status_filter = request.query_params.get('attendance_status')

        result = []

        for teacher in teacher_qs:
            att_qs = teacher.attendances.all()

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
                "teacher": _teacher_info(teacher),
                "total_records": att_qs.count(),
                "history": build_history(att_qs),
            })

        return Response(
            {
                "status": True,
                "total_teachers": len(result),
                "teachers": result,
            },
            status=status.HTTP_200_OK
        )


# =========================================================
#  DETAIL — Single teacher full history
# =========================================================
class TeacherAttendanceDetailView(APIView):
    def get(self, request, teacher_id):
        try:
            teacher = Teacher.objects.select_related('school').get(pk=teacher_id)
        except Teacher.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "error": f"Teacher with id '{teacher_id}' not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        att_qs = teacher.attendances.all()

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
                "teacher": _teacher_info(teacher),
                "total_records": att_qs.count(),
                "history": build_history(att_qs),
            },
            status=status.HTTP_200_OK
        )


# =========================================================
#  DELETE — by teacher_id + date
# =========================================================
class TeacherAttendanceDeleteView(APIView):
    def delete(self, request, teacher_id, date):
        try:
            teacher = Teacher.objects.select_related('school').get(pk=teacher_id)
        except Teacher.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "error": f"Teacher with id '{teacher_id}' not found."
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
            att = TeacherAttendance.objects.get(teacher=teacher, date=date_obj)
        except TeacherAttendance.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "error": f"No attendance found for teacher id '{teacher_id}' on {date}."
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
                    "teacher": _teacher_info(teacher),
                    "attendance": deleted_attendance,
                },
            },
            status=status.HTTP_200_OK
        )


# =========================================================
#  CHECK-IN (simple response — same 6 fields)
# =========================================================
class TeacherCheckInView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        teacher_id = request.data.get('teacher_id')
        if not teacher_id:
            return Response(
                {"status": False, "message": "teacher_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            teacher = Teacher.objects.select_related('school').get(pk=teacher_id)
        except (Teacher.DoesNotExist, ValueError):
            return Response(
                {"status": False, "message": f"Teacher with id='{teacher_id}' not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        today = timezone.localtime(timezone.now()).date()

        attendance, _ = TeacherAttendance.objects.get_or_create(
            teacher=teacher, date=today
        )

        if attendance.check_in_time:
            return Response(
                {
                    "status": False,
                    "message": "You have already checked in today.",
                    "teacher": _teacher_info(teacher),
                    "attendance": {
                        "id": attendance.id,
                        "date": attendance.date.strftime('%Y-%m-%d'),
                        "day_name": attendance.date.strftime('%A'),
                        "attendance_status": attendance.attendance_status,
                        "remarks": attendance.remarks or '',
                        "created_at": attendance.created_at,
                        "updated_at": attendance.updated_at,
                    },
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        attendance.check_in_time = timezone.now()
        attendance.ip_address = request.META.get('REMOTE_ADDR')
        attendance.remarks = request.data.get('remarks', '')
        attendance.attendance_status = 'present'
        attendance.save()

        return Response(
            {
                "status": True,
                "message": "Check-in successful.",
                "teacher": _teacher_info(teacher),
                "attendance": {
                    "id": attendance.id,
                    "date": attendance.date.strftime('%Y-%m-%d'),
                    "day_name": attendance.date.strftime('%A'),
                    "attendance_status": attendance.attendance_status,
                    "remarks": attendance.remarks or '',
                    "created_at": attendance.created_at,
                    "updated_at": attendance.updated_at,
                },
            },
            status=status.HTTP_201_CREATED
        )


# =========================================================
#  CHECK-OUT
# =========================================================
class TeacherCheckOutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        teacher_id = request.data.get('teacher_id')
        if not teacher_id:
            return Response(
                {"status": False, "message": "teacher_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            teacher = Teacher.objects.select_related('school').get(pk=teacher_id)
        except (Teacher.DoesNotExist, ValueError):
            return Response(
                {"status": False, "message": f"Teacher with id='{teacher_id}' not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        today = timezone.localtime(timezone.now()).date()

        try:
            attendance = TeacherAttendance.objects.get(teacher=teacher, date=today)
        except TeacherAttendance.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": f"No attendance record found for today ({today}). Please check-in first.",
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if not attendance.check_in_time:
            return Response(
                {"status": False, "message": "Please check-in first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if attendance.check_out_time:
            return Response(
                {
                    "status": False,
                    "message": "You have already checked out today.",
                    "teacher": _teacher_info(teacher),
                    "attendance": {
                        "id": attendance.id,
                        "date": attendance.date.strftime('%Y-%m-%d'),
                        "day_name": attendance.date.strftime('%A'),
                        "attendance_status": attendance.attendance_status,
                        "remarks": attendance.remarks or '',
                        "created_at": attendance.created_at,
                        "updated_at": attendance.updated_at,
                    },
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        attendance.check_out_time = timezone.now()
        attendance.save()

        return Response(
            {
                "status": True,
                "message": "Check-out successful.",
                "teacher": _teacher_info(teacher),
                "attendance": {
                    "id": attendance.id,
                    "date": attendance.date.strftime('%Y-%m-%d'),
                    "day_name": attendance.date.strftime('%A'),
                    "attendance_status": attendance.attendance_status,
                    "remarks": attendance.remarks or '',
                    "created_at": attendance.created_at,
                    "updated_at": attendance.updated_at,
                },
            },
            status=status.HTTP_200_OK
        )


# =========================================================
#  TODAY
# =========================================================
class TodayAttendanceView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        teacher_id = request.query_params.get('teacher_id')
        if not teacher_id:
            return Response(
                {"status": False, "message": "teacher_id query param is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            teacher = Teacher.objects.select_related('school').get(pk=teacher_id)
        except (Teacher.DoesNotExist, ValueError):
            return Response(
                {"status": False, "message": f"Teacher with id='{teacher_id}' not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        today = timezone.localtime(timezone.now()).date()

        try:
            attendance = TeacherAttendance.objects.get(teacher=teacher, date=today)
            return Response(
                {
                    "status": True,
                    "message": "Today's attendance record found.",
                    "teacher": _teacher_info(teacher),
                    "attendance": {
                        "id": attendance.id,
                        "date": attendance.date.strftime('%Y-%m-%d'),
                        "day_name": attendance.date.strftime('%A'),
                        "attendance_status": attendance.attendance_status,
                        "remarks": attendance.remarks or '',
                        "created_at": attendance.created_at,
                        "updated_at": attendance.updated_at,
                    },
                },
                status=status.HTTP_200_OK
            )
        except TeacherAttendance.DoesNotExist:
            return Response(
                {
                    "status": True,
                    "message": "No attendance record found for today.",
                    "teacher": _teacher_info(teacher),
                    "attendance": None,
                },
                status=status.HTTP_200_OK
            )


# =========================================================
#  MY HISTORY (with virtual fill for missing dates)
# =========================================================
class MyAttendanceHistoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        teacher_id = request.query_params.get('teacher_id')
        if not teacher_id:
            return Response(
                {"status": False, "message": "teacher_id query param is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            teacher = Teacher.objects.select_related('school').get(pk=teacher_id)
        except (Teacher.DoesNotExist, ValueError):
            return Response(
                {"status": False, "message": f"Teacher with id='{teacher_id}' not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        from_param = request.query_params.get('from')
        to_param = request.query_params.get('to')

        records_qs = TeacherAttendance.objects.filter(teacher=teacher).order_by('-date')
        today = timezone.localtime(timezone.now()).date()

        parsed_from = parsed_to = None
        if from_param:
            try:
                parsed_from = datetime.strptime(from_param, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {"status": False, "message": "from must be YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if to_param:
            try:
                parsed_to = datetime.strptime(to_param, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {"status": False, "message": "to must be YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        real_records = list(records_qs)
        existing_dates = {r.date for r in real_records}

        if parsed_from and parsed_to:
            range_start, range_end = parsed_from, parsed_to
        elif parsed_from:
            range_start, range_end = parsed_from, today
        elif parsed_to:
            dates = [r.date for r in real_records] + [parsed_to]
            range_start, range_end = min(dates), parsed_to
        else:
            range_start = min((r.date for r in real_records), default=None)
            range_end = today

        virtual_records = []
        if range_start is not None:
            cursor = range_start
            while cursor <= range_end:
                if cursor not in existing_dates:
                    is_week_off = (cursor.weekday() == 6)
                    virtual_records.append({
                        "id": None,
                        "date": cursor.strftime('%Y-%m-%d'),
                        "day_name": cursor.strftime('%A'),
                        "month": cursor.strftime('%B'),
                        "year": cursor.year,
                        "attendance_status": 'leave' if is_week_off else 'absent',
                        "remarks": 'auto',
                        "created_at": None,
                        "updated_at": None,
                    })
                cursor += timedelta(days=1)

        all_records = []
        for att in real_records:
            all_records.append({
                "id": att.id,
                "date": att.date.strftime('%Y-%m-%d'),
                "day_name": att.date.strftime('%A'),
                "month": att.date.strftime('%B'),
                "year": att.date.year,
                "attendance_status": att.attendance_status,
                "remarks": att.remarks or '',
                "created_at": att.created_at,
                "updated_at": att.updated_at,
            })
        all_records.extend(virtual_records)

        all_records.sort(key=lambda r: r['date'], reverse=True)

        history = {}
        for rec in all_records:
            year = str(rec['year'])
            month = rec['month']
            history.setdefault(year, {}).setdefault(month, []).append(rec)

        return Response(
            {
                "status": True,
                "teacher": _teacher_info(teacher),
                "total_records": len(all_records),
                "real_records": len(real_records),
                "history": history,
            },
            status=status.HTTP_200_OK
        )