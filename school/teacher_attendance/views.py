from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta

from .models import TeacherAttendance
from .serializers import TeacherAttendanceSerializer

User = get_user_model()


# ============================
# HELPER — Serializer for attendance (without user info)
# ============================
def attendance_data(rec):
    """Return only attendance-related fields, no user info."""
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


# ============================
# HELPER — Get or Create Teacher (No Unique Name Constraint)
# ============================
def get_or_create_teacher(request):
    teacher_id = request.data.get('teacher_id')
    teacher_name = request.data.get('teacher_name')

    if not teacher_id:
        return None, Response({
            "status": False,
            "message": "teacher_id is required."
        }, status=status.HTTP_400_BAD_REQUEST)

    # 1. Pehle ID se dhundhne ki koshish karein
    try:
        teacher = User.objects.get(id=teacher_id)
        return teacher, None
    except User.DoesNotExist:
        pass

    # 2. Agar ID na mile, toh Name check karein (naya teacher create karne ke liye)
    if not teacher_name:
        return None, Response({
            "status": False,
            "message": f"Teacher with id={teacher_id} not found. Send teacher_name to create a new one."
        }, status=status.HTTP_404_NOT_FOUND)

    # 3. Naya user create karein (Bina username unique check ke)
    # Kyunki same naam ke multiple teachers ho sakte hain
    teacher = User.objects.create(
        username=teacher_name,
        first_name=teacher_name,
        is_staff=False,
    )

    return teacher, None


# ============================
# 1. CHECK IN
# ============================
class TeacherCheckInView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        teacher, error = get_or_create_teacher(request)
        if error:
            return error

        today = timezone.localtime(timezone.now()).date()  # FIXED: Local date use karein

        attendance, created = TeacherAttendance.objects.get_or_create(
            teacher=teacher,
            date=today
        )

        if attendance.check_in_time:
            return Response({
                "status": False,
                "message": "You have already checked in today.",
                "teacher_id": teacher.id,
                "teacher_name": teacher.username,
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
            "teacher_id": teacher.id,
            "teacher_name": teacher.username,
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

        try:
            teacher = User.objects.get(id=teacher_id)
        except User.DoesNotExist:
            return Response({
                "status": False,
                "message": f"Teacher with id={teacher_id} not found. Please check-in first."
            }, status=status.HTTP_404_NOT_FOUND)

        # --- FIXED: Local date use karein (Timezone issue solved) ---
        today = timezone.localtime(timezone.now()).date()

        try:
            attendance = TeacherAttendance.objects.get(
                teacher=teacher,
                date=today
            )
        except TeacherAttendance.DoesNotExist:
            # Agar aaj ka record nahi mila, toh check karein ki kal ka toh nahi hai
            # (Sirf debugging ke liye, agar user ne raat ko check-in kiya ho)
            yesterday = today - timedelta(days=1)
            try:
                attendance = TeacherAttendance.objects.get(
                    teacher=teacher,
                    date=yesterday
                )
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
                "teacher_id": teacher.id,
                "teacher_name": teacher.username,
                "data": attendance_data(attendance)
            }, status=status.HTTP_400_BAD_REQUEST)

        attendance.check_out_time = timezone.now()

        # Working hours calculate karke status update karein
        if attendance.working_hours < 4:
            attendance.status = 'HALF_DAY'

        attendance.save()

        return Response({
            "status": True,
            "message": "Check-out successful.",
            "teacher_id": teacher.id,
            "teacher_name": teacher.username,
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

        try:
            teacher = User.objects.get(id=teacher_id)
        except User.DoesNotExist:
            return Response({
                "status": False,
                "message": f"Teacher with id={teacher_id} not found."
            }, status=status.HTTP_404_NOT_FOUND)

        today = timezone.localtime(timezone.now()).date()  # FIXED

        try:
            attendance = TeacherAttendance.objects.get(
                teacher=teacher,
                date=today
            )
            return Response({
                "status": True,
                "message": "Today's attendance record found.",
                "teacher_id": teacher.id,
                "teacher_name": teacher.username,
                "data": attendance_data(attendance)
            }, status=status.HTTP_200_OK)

        except TeacherAttendance.DoesNotExist:
            return Response({
                "status": False,
                "message": "No attendance record found for today.",
                "teacher_id": teacher.id,
                "teacher_name": teacher.username,
                "data": None
            }, status=status.HTTP_200_OK)


# ============================
# 4. OVERALL HISTORY (Year + Month wise grouped)
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

        try:
            teacher = User.objects.get(id=teacher_id)
        except User.DoesNotExist:
            return Response({
                "status": False,
                "message": f"Teacher with id={teacher_id} not found."
            }, status=status.HTTP_404_NOT_FOUND)

        records = TeacherAttendance.objects.filter(teacher=teacher).order_by('-date')

        grouped = {}
        for rec in records:
            year = rec.date.year
            month = rec.date.strftime("%B")

            if year not in grouped:
                grouped[year] = {}
            if month not in grouped[year]:
                grouped[year][month] = []

            grouped[year][month].append({
                "id": rec.id,
                "date": rec.date.strftime("%Y-%m-%d"),
                "day_name": rec.date.strftime("%A"),
                "check_in_time": rec.check_in_time.strftime("%I:%M %p") if rec.check_in_time else None,
                "check_out_time": rec.check_out_time.strftime("%I:%M %p") if rec.check_out_time else None,
                "status": rec.status,
                "working_hours": rec.working_hours,
                "remarks": rec.remarks,
            })

        return Response({
            "status": True,
            "teacher_id": teacher.id,
            "teacher_name": teacher.username,
            "total_records": records.count(),
            "history": grouped,
        }, status=status.HTTP_200_OK)


# ============================
# 5. DETAIL — Get single attendance by ID
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
            "teacher_id": attendance.teacher.id,
            "teacher_name": attendance.teacher.username,
            "data": attendance_data(attendance)
        }, status=status.HTTP_200_OK)


# ============================
# 6. UPDATE — Update attendance by ID
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
            if data['status'] not in ['PRESENT', 'ABSENT', 'HALF_DAY', 'LEAVE', 'LATE']:
                return Response({
                    "status": False,
                    "message": "Invalid status. Use: PRESENT, ABSENT, HALF_DAY, LEAVE, LATE."
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
            "teacher_id": attendance.teacher.id,
            "teacher_name": attendance.teacher.username,
            "data": attendance_data(attendance)
        }, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        return self.put(request, pk)


# ============================
# 7. DELETE — Delete attendance by ID
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

        teacher_id = attendance.teacher.id
        teacher_name = attendance.teacher.username
        attendance.delete()

        return Response({
            "status": True,
            "message": "Attendance deleted successfully.",
            "teacher_id": teacher_id,
            "teacher_name": teacher_name,
            "deleted_id": pk
        }, status=status.HTTP_200_OK)