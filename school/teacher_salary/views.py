# school/teacher_salary/views.py
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from django.shortcuts import get_object_or_404

from school.school_type.models import SchoolType
from school.teacher.models import Teacher
from .models import TeacherSalary
from .serializers import TeacherSalarySerializer, TeacherSalaryListSerializer

logger = logging.getLogger(__name__)

MONTHS_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def _get_teacher_by_card(teacher_id_card):
    try:
        return Teacher.objects.get(teacher_id_card=teacher_id_card)
    except Teacher.DoesNotExist:
        return None


# =====================================================================
# 1. LIST ALL TEACHERS (with salary summary) - ALL SCHOOLS
#    GET /api/v1/school/teacher/salary/list/
# =====================================================================
class TeacherSalaryListView(APIView):
    def get(self, request):
        teachers = Teacher.objects.select_related("school").all().order_by("-id")
        serializer = TeacherSalaryListSerializer(teachers, many=True)

        return Response(
            {
                "success": True,
                "count": teachers.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# =====================================================================
# 2. LIST TEACHERS BY SCHOOL (with salary summary)
#    GET /api/v1/school/teacher/salary/list/school/<school_id>/
# =====================================================================
class TeacherSalaryListBySchoolView(APIView):
    def get(self, request, school_id):
        school = get_object_or_404(SchoolType, pk=school_id)
        teachers = Teacher.objects.filter(school=school).select_related("school").order_by("-id")

        if not teachers.exists():
            return Response(
                {
                    "success": False,
                    "message": f"No teachers found for school id '{school_id}'",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TeacherSalaryListSerializer(teachers, many=True)

        return Response(
            {
                "success": True,
                "school_id": school.id,
                "school_name": school.school_name,
                "count": teachers.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# =====================================================================
# 3. TEACHER SALARY SUMMARY (GET + POST)
#    GET  /api/v1/school/teacher/salary/summary/<teacher_id_card>/
#    POST /api/v1/school/teacher/salary/summary/<teacher_id_card>/
# =====================================================================
class TeacherSalarySummaryView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, teacher_id_card):
        teacher = _get_teacher_by_card(teacher_id_card)
        if not teacher:
            return Response(
                {"success": False, "message": "Teacher not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        qs = TeacherSalary.objects.filter(teacher=teacher).order_by("-year", "-id")

        years_map = {}
        for s in qs:
            year = (s.year or "Unknown").strip()
            month_key = (s.month or "Unknown").strip().title()
            years_map.setdefault(year, {})
            years_map[year].setdefault(month_key, [])
            years_map[year][month_key].append(s)

        years_data = []
        for year in sorted(years_map.keys(), reverse=True):
            months_data = []
            for month in MONTHS_ORDER:
                if month in years_map[year]:
                    records = years_map[year][month]
                    total = sum(float(r.amount or 0) for r in records)
                    paid = sum(float(r.paid_amount or 0) for r in records)
                    pending = sum(float(r.pending_amount or 0) for r in records)

                    months_data.append({
                        "month": month,
                        "total_salary": total,
                        "paid_amount": paid,
                        "pending_amount": pending,
                        "records": TeacherSalarySerializer(records, many=True).data,
                    })

            for month_key in years_map[year].keys():
                if month_key not in MONTHS_ORDER:
                    records = years_map[year][month_key]
                    total = sum(float(r.amount or 0) for r in records)
                    paid = sum(float(r.paid_amount or 0) for r in records)
                    pending = sum(float(r.pending_amount or 0) for r in records)

                    months_data.append({
                        "month": month_key,
                        "total_salary": total,
                        "paid_amount": paid,
                        "pending_amount": pending,
                        "records": TeacherSalarySerializer(records, many=True).data,
                    })

            years_data.append({
                "year": year,
                "total_salary": sum(m["total_salary"] for m in months_data),
                "paid_amount": sum(m["paid_amount"] for m in months_data),
                "pending_amount": sum(m["pending_amount"] for m in months_data),
                "months": months_data,
            })

        latest = qs.first()
        latest_data = TeacherSalarySerializer(latest).data if latest else None

        all_total = sum(float(s.amount or 0) for s in qs)
        all_paid = sum(float(s.paid_amount or 0) for s in qs)
        all_pending = sum(float(s.pending_amount or 0) for s in qs)

        return Response(
            {
                "success": True,
                "data": {
                    "teacher_id_card": teacher.teacher_id_card,
                    "teacher_name": f"{teacher.first_name} {teacher.last_name}",
                    "school_id": teacher.school.id if teacher.school else None,
                    "school_name": teacher.school.school_name if teacher.school else None,
                    "total_salary": all_total,
                    "paid_amount": all_paid,
                    "pending_amount": all_pending,
                    "latest_salary": latest_data,
                    "years": years_data,
                },
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, teacher_id_card):
        teacher = _get_teacher_by_card(teacher_id_card)
        if not teacher:
            return Response(
                {"success": False, "message": "Teacher not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        month = request.data.get("month")
        year = request.data.get("year")
        payment_method = request.data.get("payment_method", "Cash")
        amount = request.data.get("amount", 0)
        paid_amount = request.data.get("paid_amount", 0)
        paid_date = request.data.get("paid_date")
        remark = request.data.get("remark", "")

        if not month or not year:
            return Response(
                {"success": False, "message": "month and year are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        valid_methods = ["Cash", "Bank", "UPI", "Cheque", "Bank Transfer"]
        if payment_method not in valid_methods:
            return Response(
                {"success": False, "message": f"payment_method must be one of {valid_methods}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            amount = float(amount)
            paid_amount = float(paid_amount)
        except (TypeError, ValueError):
            return Response(
                {"success": False, "message": "amount and paid_amount must be numbers"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        salary = TeacherSalary.objects.create(
            teacher=teacher,
            month=month,
            year=str(year),
            payment_method=payment_method,
            amount=amount,
            paid_amount=paid_amount,
            paid_date=paid_date,
            remark=remark,
        )

        return Response(
            {
                "success": True,
                "message": "Salary payment saved successfully",
                "data": TeacherSalarySerializer(salary).data,
            },
            status=status.HTTP_201_CREATED,
        )


# =====================================================================
# 4. DELETE SALARY BY MONTH + YEAR
#    DELETE /api/v1/school/teacher/salary/summary/<teacher_id_card>/<year>/<month>/
# =====================================================================
class TeacherSalaryDeleteMonthView(APIView):
    def delete(self, request, teacher_id_card, year, month):
        teacher = _get_teacher_by_card(teacher_id_card)
        if not teacher:
            return Response(
                {"success": False, "message": "Teacher not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        month_key = (month or "").strip().title()
        year_key = str(year).strip()

        qs = TeacherSalary.objects.filter(
            teacher=teacher,
            year=year_key,
            month__iexact=month_key,
        )

        count = qs.count()
        if count == 0:
            return Response(
                {
                    "success": False,
                    "message": f"No salary records found for {month_key} {year_key}",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        deleted_ids = list(qs.values_list("id", flat=True))
        qs.delete()

        return Response(
            {
                "success": True,
                "message": f"Deleted {count} salary record(s) for {month_key} {year_key}",
                "data": {
                    "teacher_id_card": teacher.teacher_id_card,
                    "year": year_key,
                    "month": month_key,
                    "deleted_count": count,
                    "deleted_ids": deleted_ids,
                },
            },
            status=status.HTTP_200_OK,
        )