from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta

from .models import TeacherAttendance

User = get_user_model()


# ============================
# HELPER — Attendance Data
# ============================
def attendance_data(rec):
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
    }


def virtual_attendance_data(date_obj, status_value):
    """Ek aisa record return karta hai jo DB me nahi hai — sirf response me bhejne ke liye."""
    return {
        "id": None,
        "date": date_obj.strftime("%Y-%m-%d"),
        "day_name": date_obj.strftime("%A"),
        "month": date_obj.strftime("%B"),
        "year": date_obj.year,
        "check_in_time": None,
        "check_out_time": None,
        "status": status_value,      # 'ABSENT' or 'WEEK_OFF'
        "working_hours": 0.0,
        "remarks": "auto",
    }


# ============================
# HELPER — Get or Create Teacher
# ============================
def get_or_create_teacher(teacher_id):
    if not teacher_id:
        return None, "teacher_id is required."

    teacher_id = str(teacher_id).strip()

    try:
        teacher = User.objects.get(username=teacher_id)
        return teacher, None
    except User.DoesNotExist:
        pass

    teacher = User.objects.create_user(
        username=teacher_id,
        first_name=teacher_id,
        password=None,
        is_staff=False,
    )
    return teacher, None


# ============================
# HELPER — Fill Missing Dates (ABSENT / WEEK_OFF)
# ============================
def fill_missing_dates(records, start_date, end_date, week_off_day=6):
    """
    records: list of dicts (already serialized). Each must have 'date' key (YYYY-MM-DD).
    start_date: datetime.date — earliest record date
    end_date: datetime.date — today (inclusive)
    week_off_day: 0=Mon ... 6=Sun (default Sunday=6)

    Returns:
      - merged list sorted by date DESC (newest first)
    """
    existing_dates = {rec['date'] for rec in records}

    filled = list(records)
    cursor = start_date

    while cursor <= end_date:
        date_str = cursor.strftime("%Y-%m-%d")

        if date_str not in existing_dates:
            is_week_off = (cursor.weekday() == week_off_day)
            status_value = 'WEEK_OFF' if is_week_off else 'ABSENT'
            filled.append(virtual_attendance_data(cursor, status_value))

        cursor += timedelta(days=1)

    # Newest first
    filled.sort(key=lambda r: r['date'], reverse=True)
    return filled


# ============================
# 1. CHECK IN
# ============================
class TeacherCheckInView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        teacher_id = request.data.get('teacher_id')

        teacher, error = get_or_create_teacher(teacher_id)
        if error:
            return Response({
                "status": False,
                "message": error
            }, status=status.HTTP_400_BAD_REQUEST)

        today = timezone.localtime(timezone.now()).date()

        attendance, created = TeacherAttendance.objects.get_or_create(
            teacher=teacher,
            date=today
        )

        if attendance.check_in_time:
            return Response({
                "status": False,
                "message": "You have already checked in today.",
                "teacher_id": teacher.username,
                "data": attendance_data(attendance)
            }, status=status.HTTP_400_BAD_REQUEST)

        attendance.check_in_time = timezone.now()
        attendance.ip_address = request.META.get('REMOTE_ADDR')
        attendance.remarks = request.data.get('remarks', '')

        if (attendance.check_in_time.hour > 9) or \
           (attendance.check_in_time.hour == 9 and attendance.check_in_time.minute > 30):
            attendance.status = 'LATE'
        else:
            attendance.status = 'PRESENT'

        attendance.save()

        return Response({
            "status": True,
            "message": "Check-in successful.",
            "teacher_id": teacher.username,
            "data": attendance_data(attendance)
        }, status=status.HTTP_201_CREATED)


# ============================
# 2. CHECK OUT
# ============================
class TeacherCheckOutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        teacher_id = request.data.get('teacher_id')

        if not teacher_id:
            return Response({
                "status": False,
                "message": "teacher_id is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        teacher_id = str(teacher_id).strip()

        try:
            teacher = User.objects.get(username=teacher_id)
        except User.DoesNotExist:
            return Response({
                "status": False,
                "message": f"Teacher with id='{teacher_id}' not found. Please check-in first."
            }, status=status.HTTP_404_NOT_FOUND)

        today = timezone.localtime(timezone.now()).date()

        try:
            attendance = TeacherAttendance.objects.get(
                teacher=teacher,
                date=today
            )
        except TeacherAttendance.DoesNotExist:
            yesterday = today - timedelta(days=1)
            try:
                TeacherAttendance.objects.get(teacher=teacher, date=yesterday)
                return Response({
                    "status": False,
                    "message": f"Attendance record found for {yesterday}, but not for today ({today}). Please check your Timezone settings."
                }, status=status.HTTP_400_BAD_REQUEST)
            except TeacherAttendance.DoesNotExist:
                return Response({
                    "status": False,
                    "message": f"No attendance record found for today ({today}). Please check-in first."
                }, status=status.HTTP_404_NOT_FOUND)

        if not attendance.check_in_time:
            return Response({
                "status": False,
                "message": "Please check-in first."
            }, status=status.HTTP_400_BAD_REQUEST)

        if attendance.check_out_time:
            return Response({
                "status": False,
                "message": "You have already checked out today.",
                "teacher_id": teacher.username,
                "data": attendance_data(attendance)
            }, status=status.HTTP_400_BAD_REQUEST)

        attendance.check_out_time = timezone.now()

        if attendance.working_hours < 4:
            attendance.status = 'HALF_DAY'

        attendance.save()

        return Response({
            "status": True,
            "message": "Check-out successful.",
            "teacher_id": teacher.username,
            "data": attendance_data(attendance)
        }, status=status.HTTP_200_OK)


# ============================
# 3. TODAY ATTENDANCE
# ============================
class TodayAttendanceView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        teacher_id = request.query_params.get('teacher_id')

        if not teacher_id:
            return Response({
                "status": False,
                "message": "teacher_id query param is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        teacher_id = str(teacher_id).strip()

        try:
            teacher = User.objects.get(username=teacher_id)
        except User.DoesNotExist:
            return Response({
                "status": False,
                "message": f"Teacher with id='{teacher_id}' not found."
            }, status=status.HTTP_404_NOT_FOUND)

        today = timezone.localtime(timezone.now()).date()

        try:
            attendance = TeacherAttendance.objects.get(teacher=teacher, date=today)
            return Response({
                "status": True,
                "message": "Today's attendance record found.",
                "teacher_id": teacher.username,
                "data": attendance_data(attendance)
            }, status=status.HTTP_200_OK)
        except TeacherAttendance.DoesNotExist:
            return Response({
                "status": False,
                "message": "No attendance record found for today.",
                "teacher_id": teacher.username,
                "data": None
            }, status=status.HTTP_200_OK)


# ============================
# 4. OVERALL HISTORY  ⭐ UPDATED
# ============================
class MyAttendanceHistoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        teacher_id = request.query_params.get('teacher_id')

        if not teacher_id:
            return Response({
                "status": False,
                "message": "teacher_id query param is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        teacher_id = str(teacher_id).strip()

        try:
            teacher = User.objects.get(username=teacher_id)
        except User.DoesNotExist:
            return Response({
                "status": False,
                "message": f"Teacher with id='{teacher_id}' not found."
            }, status=status.HTTP_404_NOT_FOUND)

        # Optional query param: ?month=2026-09  (for testing specific month)
        # Optional query param: ?from=2026-09-01&to=2026-09-23
        from_param = request.query_params.get('from')
        to_param = request.query_params.get('to')

        records_qs = TeacherAttendance.objects.filter(teacher=teacher).order_by('-date')

        today = timezone.localtime(timezone.now()).date()

        # ---------- Resolve range ----------
        parsed_from = None
        parsed_to = None

        if from_param:
            try:
                parsed_from = datetime.strptime(from_param, "%Y-%m-%d").date()
            except ValueError:
                return Response({
                    "status": False,
                    "message": "from must be YYYY-MM-DD"
                }, status=status.HTTP_400_BAD_REQUEST)

        if to_param:
            try:
                parsed_to = datetime.strptime(to_param, "%Y-%m-%d").date()
            except ValueError:
                return Response({
                    "status": False,
                    "message": "to must be YYYY-MM-DD"
                }, status=status.HTTP_400_BAD_REQUEST)

        # ---------- Build flat list of real records ----------
        flat_records = []
        for rec in records_qs:
            flat_records.append({
                "id": rec.id,
                "date": rec.date.strftime("%Y-%m-%d"),
                "day_name": rec.date.strftime("%A"),
                "check_in_time": rec.check_in_time.strftime("%I:%M %p") if rec.check_in_time else None,
                "check_out_time": rec.check_out_time.strftime("%I:%M %p") if rec.check_out_time else None,
                "status": rec.status,
                "working_hours": rec.working_hours,
                "remarks": rec.remarks,
            })

        # ---------- Decide the fill range ----------
        # Priority: from/to params > earliest record > today
        if parsed_from and parsed_to:
            range_start = parsed_from
            range_end = parsed_to
        elif parsed_from:
            range_start = parsed_from
            range_end = today
        elif parsed_to:
            # start = earliest real record (or to_param itself if no records)
            range_start = min([r for r in [rec.date for rec in records_qs]] + [parsed_to])
            range_end = parsed_to
        else:
            # No params: fill from earliest record till today
            if flat_records:
                earliest = min(rec.date for rec in records_qs)
                range_start = earliest
            else:
                # No records at all — skip filling
                range_start = None
            range_end = today

        # ---------- Fill missing dates ----------
        if range_start is not None:
            flat_records = fill_missing_dates(
                records=flat_records,
                start_date=range_start,
                end_date=range_end,
                week_off_day=6,   # Sunday
            )
        else:
            flat_records.sort(key=lambda r: r['date'], reverse=True)

        # ---------- Re-group by year → month ----------
        grouped = {}
        for rec in flat_records:
            date_obj = datetime.strptime(rec['date'], "%Y-%m-%d").date()
            year = date_obj.year
            month = date_obj.strftime("%B")

            grouped.setdefault(year, {}).setdefault(month, []).append(rec)

        return Response({
            "status": True,
            "teacher_id": teacher.username,
            "total_records": len(flat_records),   # 👈 includes virtuals
            "real_records": records_qs.count(),   # 👈 only DB records
            "history": grouped,
        }, status=status.HTTP_200_OK)


# ============================
# 5. DETAIL
# ============================
class AttendanceDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            attendance = TeacherAttendance.objects.get(id=pk)
        except TeacherAttendance.DoesNotExist:
            return Response({
                "status": False,
                "message": f"Attendance with id={pk} not found."
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "status": True,
            "message": "Attendance record found.",
            "teacher_id": attendance.teacher.username,
            "data": attendance_data(attendance)
        }, status=status.HTTP_200_OK)


# ============================
# 6. UPDATE
# ============================
class AttendanceUpdateView(APIView):
    permission_classes = [AllowAny]

    def put(self, request, pk):
        try:
            attendance = TeacherAttendance.objects.get(id=pk)
        except TeacherAttendance.DoesNotExist:
            return Response({
                "status": False,
                "message": f"Attendance with id={pk} not found."
            }, status=status.HTTP_404_NOT_FOUND)

        data = request.data

        if 'remarks' in data:
            attendance.remarks = data['remarks']

        if 'status' in data:
            if data['status'] not in ['PRESENT', 'ABSENT', 'HALF_DAY', 'LEAVE', 'LATE', 'WEEK_OFF']:
                return Response({
                    "status": False,
                    "message": "Invalid status."
                }, status=status.HTTP_400_BAD_REQUEST)
            attendance.status = data['status']

        if 'check_in_time' in data and data['check_in_time']:
            try:
                attendance.check_in_time = datetime.strptime(
                    data['check_in_time'], "%Y-%m-%d %H:%M:%S"
                )
            except ValueError:
                return Response({
                    "status": False,
                    "message": "check_in_time format must be 'YYYY-MM-DD HH:MM:SS'."
                }, status=status.HTTP_400_BAD_REQUEST)

        if 'check_out_time' in data and data['check_out_time']:
            try:
                attendance.check_out_time = datetime.strptime(
                    data['check_out_time'], "%Y-%m-%d %H:%M:%S"
                )
            except ValueError:
                return Response({
                    "status": False,
                    "message": "check_out_time format must be 'YYYY-MM-DD HH:MM:SS'."
                }, status=status.HTTP_400_BAD_REQUEST)

        attendance.save()

        return Response({
            "status": True,
            "message": "Attendance updated successfully.",
            "teacher_id": attendance.teacher.username,
            "data": attendance_data(attendance)
        }, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        return self.put(request, pk)


# ============================
# 7. DELETE
# ============================
class AttendanceDeleteView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, pk):
        try:
            attendance = TeacherAttendance.objects.get(id=pk)
        except TeacherAttendance.DoesNotExist:
            return Response({
                "status": False,
                "message": f"Attendance with id={pk} not found."
            }, status=status.HTTP_404_NOT_FOUND)

        teacher_id = attendance.teacher.username
        attendance.delete()

        return Response({
            "status": True,
            "message": "Attendance deleted successfully.",
            "teacher_id": teacher_id,
            "deleted_id": pk
        }, status=status.HTTP_200_OK)