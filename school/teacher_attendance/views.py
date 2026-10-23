from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from school.teacher.models import Teacher
from school.teacher.serializers import TeacherSerializer
from .models import TeacherAttendance


def get_teacher_by_id(teacher_id):
    if not teacher_id:
        return None, "teacher_id is required."
    try:
        teacher = Teacher.objects.select_related('school').get(id=teacher_id)
        return teacher, None
    except Teacher.DoesNotExist:
        return None, f"Teacher with id={teacher_id} not found."


def attendance_to_dict(rec):
    return {
        "id": rec.id,
        "date": rec.date.strftime("%Y-%m-%d"),
        "day_name": rec.date.strftime("%A"),
        "month": rec.date.strftime("%B"),
        "year": rec.date.year,
        "check_in_time": rec.check_in_time.strftime("%I:%M %p") if rec.check_in_time else None,
        "check_out_time": rec.check_out_time.strftime("%I:%M %p") if rec.check_out_time else None,
        "status": rec.status,
        "working_hours": rec.working_hours,
        "remarks": rec.remarks,
        "is_virtual": False,
    }


def virtual_to_dict(date_obj, status_value):
    return {
        "id": None,
        "date": date_obj.strftime("%Y-%m-%d"),
        "day_name": date_obj.strftime("%A"),
        "month": date_obj.strftime("%B"),
        "year": date_obj.year,
        "check_in_time": None,
        "check_out_time": None,
        "status": status_value,
        "working_hours": 0.0,
        "remarks": "auto",
        "is_virtual": True,
    }


def fill_missing(records, start_date, end_date):
    existing = {r['date'] for r in records}
    filled = list(records)
    cursor = start_date
    while cursor <= end_date:
        date_str = cursor.strftime("%Y-%m-%d")
        if date_str not in existing:
            filled.append(virtual_to_dict(cursor, 'absent'))
        cursor += timedelta(days=1)
    filled.sort(key=lambda r: r['date'], reverse=True)
    return filled


class TeacherAttendanceListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        school_id = request.query_params.get('school_id')
        teacher_id = request.query_params.get('teacher_id')

        qs = Teacher.objects.select_related('school').all().order_by('-id')

        if school_id:
            qs = qs.filter(school_id=school_id)
        if teacher_id:
            qs = qs.filter(id=teacher_id)

        if not qs.exists():
            return Response(
                {"success": False, "message": "No teachers found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        today = timezone.localdate()
        result = []

        for teacher in qs:
            try:
                rec = TeacherAttendance.objects.get(teacher=teacher, date=today)
                today_status = rec.status
                date_str = rec.date.strftime("%Y-%m-%d")
            except TeacherAttendance.DoesNotExist:
                today_status = 'absent'
                date_str = today.strftime("%Y-%m-%d")

            result.append({
                "attendance_status": {
                    "today_is": today_status,
                    "date": date_str,
                },
                "teacher": TeacherSerializer(teacher).data,
            })

        return Response(
            {"success": True, "count": len(result), "data": result},
            status=status.HTTP_200_OK,
        )


class TeacherCheckInView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        teacher, error = get_teacher_by_id(request.data.get('teacher_id'))
        if error:
            return Response(
                {"success": False, "message": error},
                status=status.HTTP_400_BAD_REQUEST,
            )

        today = timezone.localdate()

        attendance, _ = TeacherAttendance.objects.get_or_create(
            teacher=teacher, date=today,
        )

        if attendance.check_in_time:
            return Response(
                {
                    "success": False,
                    "message": "You have already checked in today.",
                    "teacher_id": teacher.id,
                    "teacher_id_card": teacher.teacher_id_card,
                    "data": attendance_to_dict(attendance),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        attendance.check_in_time = timezone.now()
        attendance.ip_address = request.META.get('REMOTE_ADDR')
        attendance.remarks = request.data.get('remarks', '')
        attendance.status = 'present'
        attendance.save()

        return Response(
            {
                "success": True,
                "message": "Check-in successful.",
                "teacher_id": teacher.id,
                "teacher_id_card": teacher.teacher_id_card,
                "data": attendance_to_dict(attendance),
            },
            status=status.HTTP_201_CREATED,
        )


class TeacherCheckOutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        teacher, error = get_teacher_by_id(request.data.get('teacher_id'))
        if error:
            return Response(
                {"success": False, "message": error},
                status=status.HTTP_400_BAD_REQUEST,
            )

        today = timezone.localdate()

        try:
            attendance = TeacherAttendance.objects.get(teacher=teacher, date=today)
        except TeacherAttendance.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": f"No attendance record found for today ({today}). Please check-in first.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not attendance.check_in_time:
            return Response(
                {"success": False, "message": "Please check-in first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if attendance.check_out_time:
            return Response(
                {
                    "success": False,
                    "message": "You have already checked out today.",
                    "teacher_id": teacher.id,
                    "teacher_id_card": teacher.teacher_id_card,
                    "data": attendance_to_dict(attendance),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        attendance.check_out_time = timezone.now()
        attendance.status = 'present'
        attendance.save()

        return Response(
            {
                "success": True,
                "message": "Check-out successful.",
                "teacher_id": teacher.id,
                "teacher_id_card": teacher.teacher_id_card,
                "data": attendance_to_dict(attendance),
            },
            status=status.HTTP_200_OK,
        )


class TeacherAttendanceHistoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        teacher, error = get_teacher_by_id(request.query_params.get('teacher_id'))
        if error:
            return Response(
                {"success": False, "message": error},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from_param = request.query_params.get('from')
        to_param = request.query_params.get('to')
        today = timezone.localdate()

        parsed_from = parsed_to = None

        if from_param:
            try:
                parsed_from = datetime.strptime(from_param, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"success": False, "message": "from must be YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if to_param:
            try:
                parsed_to = datetime.strptime(to_param, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"success": False, "message": "to must be YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if parsed_from and parsed_to and parsed_from > parsed_to:
            return Response(
                {"success": False, "message": "from must be <= to"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        records_qs = TeacherAttendance.objects.filter(teacher=teacher).order_by('-date')
        flat_records = [attendance_to_dict(rec) for rec in records_qs]

        if parsed_from and parsed_to:
            range_start, range_end = parsed_from, parsed_to
        elif parsed_from:
            range_start, range_end = parsed_from, today
        elif parsed_to:
            earliest = min(records_qs.values_list('date', flat=True), default=parsed_to)
            range_start, range_end = min(earliest, parsed_to), parsed_to
        else:
            if records_qs.exists():
                range_start = records_qs.last().date
            else:
                range_start = None
            range_end = today

        if range_start is not None:
            flat_records = fill_missing(flat_records, range_start, range_end)
        else:
            flat_records.sort(key=lambda r: r['date'], reverse=True)

        grouped = {}
        for rec in flat_records:
            date_obj = datetime.strptime(rec['date'], "%Y-%m-%d").date()
            year_key = str(date_obj.year)
            month_key = date_obj.strftime("%B")
            grouped.setdefault(year_key, {}).setdefault(month_key, []).append(rec)

        return Response(
            {
                "success": True,
                "teacher_id": teacher.id,
                "teacher_id_card": teacher.teacher_id_card,
                "teacher_name": f"{teacher.first_name} {teacher.last_name}",
                "total_records": len(flat_records),
                "real_records": records_qs.count(),
                "history": grouped,
            },
            status=status.HTTP_200_OK,
        )


class AttendanceUpdateView(APIView):
    permission_classes = [AllowAny]

    def _update(self, request, pk=None):
        teacher_id = request.data.get('teacher_id')
        date_str = request.data.get('date')
        status_value = request.data.get('status')
        remarks = request.data.get('remarks', '')

        if not teacher_id or not date_str:
            return Response(
                {"success": False, "message": "teacher_id and date are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"success": False, "message": "date format must be YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )

        valid_statuses = [c[0] for c in TeacherAttendance.ATTENDANCE_STATUS_CHOICES]
        if status_value and status_value not in valid_statuses:
            return Response(
                {"success": False, "message": f"Invalid status. Allowed: {valid_statuses}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            teacher = Teacher.objects.get(id=teacher_id)
        except Teacher.DoesNotExist:
            return Response(
                {"success": False, "message": f"Teacher with id={teacher_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        attendance, created = TeacherAttendance.objects.get_or_create(
            teacher=teacher,
            date=date_obj,
            defaults={
                'status': status_value or 'absent',
                'remarks': remarks
            }
        )

        if not created:
            if status_value:
                attendance.status = status_value
            if remarks:
                attendance.remarks = remarks
            attendance.save()

        return Response(
            {
                "success": True,
                "message": "Attendance updated successfully." if not created else "Attendance created successfully.",
                "teacher_id": teacher.id,
                "teacher_id_card": teacher.teacher_id_card,
                "data": {
                    "id": attendance.id,
                    "date": attendance.date.strftime("%Y-%m-%d"),
                    "day_name": attendance.date.strftime("%A"),
                    "month": attendance.date.strftime("%B"),
                    "year": attendance.date.year,
                    "check_in_time": attendance.check_in_time.strftime("%I:%M %p") if attendance.check_in_time else None,
                    "check_out_time": attendance.check_out_time.strftime("%I:%M %p") if attendance.check_out_time else None,
                    "status": attendance.status,
                    "working_hours": attendance.working_hours,
                    "remarks": attendance.remarks,
                    "is_virtual": False,
                }
            },
            status=status.HTTP_200_OK
        )

    def put(self, request, pk=None):
        return self._update(request, pk)

    def patch(self, request, pk=None):
        return self._update(request, pk)


class AttendanceDeleteView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, pk):
        try:
            attendance = TeacherAttendance.objects.get(id=pk)
        except TeacherAttendance.DoesNotExist:
            return Response(
                {"success": False, "message": f"Attendance id={pk} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        card = attendance.teacher.teacher_id_card
        teacher_id = attendance.teacher.id
        attendance.delete()

        return Response(
            {
                "success": True,
                "message": "Attendance deleted successfully.",
                "teacher_id": teacher_id,
                "teacher_id_card": card,
                "deleted_id": pk,
            },
            status=status.HTTP_200_OK,
        )