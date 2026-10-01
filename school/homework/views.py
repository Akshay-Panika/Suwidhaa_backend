from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Homework
from .serializers import HomeworkSerializer, HomeworkCreateUpdateSerializer


# ═══════════════════════════════════════════════════════════
# 📌 CREATE HOMEWORK
#    POST /api/v1/school/homework/create/
# ═══════════════════════════════════════════════════════════
class HomeworkCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        try:
            serializer = HomeworkCreateUpdateSerializer(data=request.data)
            if serializer.is_valid():
                hw = serializer.save()
                return Response(
                    {
                        "success": True,
                        "message": "Homework created successfully",
                        "data": HomeworkSerializer(hw).data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                {
                    "success": False,
                    "message": "Validation failed",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"success": False, "message": f"Server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ═══════════════════════════════════════════════════════════
# 📌 LIST ALL HOMEWORK
#    GET /api/v1/school/homework/list/
# ═══════════════════════════════════════════════════════════
class HomeworkListView(APIView):

    def get(self, request):
        try:
            qs = Homework.objects.all()

            school_type = request.GET.get("school_type")
            class_name = request.GET.get("class_name")
            subject = request.GET.get("subject")
            teacher_id = request.GET.get("teacher_id")

            if school_type:
                qs = qs.filter(school_type__iexact=school_type.strip())
            if class_name:
                qs = qs.filter(class_name__iexact=class_name.strip())
            if subject:
                qs = qs.filter(subject__iexact=subject.strip())
            if teacher_id:
                qs = qs.filter(teacher_id=teacher_id)

            serializer = HomeworkSerializer(qs, many=True)
            return Response(
                {
                    "success": True,
                    "message": "Homework list fetched successfully",
                    "count": len(serializer.data),
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"success": False, "message": f"Server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ═══════════════════════════════════════════════════════════
# 📌 LIST BY SCHOOL TYPE + CLASS NAME
#    GET /api/v1/school/homework/list/<school_type>/<class_name>/
# ═══════════════════════════════════════════════════════════
class HomeworkListSchoolWithClassView(APIView):

    def get(self, request, school_type, class_name):
        try:
            qs = Homework.objects.all()

            qs = qs.filter(school_type__iexact=school_type.strip())
            qs = qs.filter(class_name__iexact=class_name.strip())

            subject = request.GET.get("subject")
            teacher_id = request.GET.get("teacher_id")

            if subject:
                qs = qs.filter(subject__iexact=subject.strip())
            if teacher_id:
                qs = qs.filter(teacher_id=teacher_id)

            serializer = HomeworkSerializer(qs, many=True)
            return Response(
                {
                    "success": True,
                    "message": "Homework list fetched successfully",
                    "school_type": school_type,
                    "class_name": class_name,
                    "count": len(serializer.data),
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"success": False, "message": f"Server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ═══════════════════════════════════════════════════════════
# ✅ NEW: LIST HOMEWORK BY TEACHER ID
#    GET /api/v1/school/homework/list/teacher-id/<teacher_id>/
# ═══════════════════════════════════════════════════════════
class HomeworkListByTeacherView(APIView):

    def get(self, request, teacher_id):
        try:
            qs = Homework.objects.filter(teacher_id=teacher_id.strip())

            # Optional extra filters via query string
            school_type = request.GET.get("school_type")
            class_name = request.GET.get("class_name")
            subject = request.GET.get("subject")

            if school_type:
                qs = qs.filter(school_type__iexact=school_type.strip())
            if class_name:
                qs = qs.filter(class_name__iexact=class_name.strip())
            if subject:
                qs = qs.filter(subject__iexact=subject.strip())

            serializer = HomeworkSerializer(qs, many=True)
            return Response(
                {
                    "success": True,
                    "message": "Homework list fetched successfully",
                    "teacher_id": teacher_id,
                    "count": len(serializer.data),
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"success": False, "message": f"Server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

# ═══════════════════════════════════════════════════════════
# 📌 TOGGLE / SET STUDENT STATUS IN HOMEWORK
# ═══════════════════════════════════════════════════════════
class HomeworkToggleStudentStatusView(APIView):
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def post(self, request, pk, student_idcard):
        try:
            try:
                hw = Homework.objects.get(pk=pk)
            except Homework.DoesNotExist:
                return Response(
                    {"success": False, "message": "Homework not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if not isinstance(hw.student_ids_list, list):
                hw.student_ids_list = []

            body = request.data or {}
            explicit = "status" in body
            found = False
            new_status = None

            for entry in hw.student_ids_list:
                if not isinstance(entry, dict):
                    continue

                card = (
                    entry.get("studentIdcard")
                    or entry.get("student_id_card")
                    or entry.get("studentId")
                    or ""
                )

                if str(card).strip() == str(student_idcard).strip():
                    current = bool(entry.get("status", False))
                    new_status = bool(body["status"]) if explicit else not current
                    entry["status"] = new_status
                    entry["studentIdcard"] = str(card).strip()
                    found = True
                    break

            if not found:
                return Response(
                    {
                        "success": False,
                        "message": f"Student {student_idcard} not assigned to this homework",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            hw.student_ids_list = hw.student_ids_list
            hw.save(update_fields=["student_ids_list", "updated_at"])

            return Response(
                {
                    "success": True,
                    "message": "Status updated",
                    "data": {
                        "homework_id": hw.id,
                        "studentIdcard": student_idcard,
                        "status": new_status,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"success": False, "message": f"Server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

# ═══════════════════════════════════════════════════════════
# 📌 GET ONE + UPDATE + DELETE HOMEWORK
# ═══════════════════════════════════════════════════════════
class HomeworkDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def _get_object(self, pk):
        try:
            return Homework.objects.get(pk=pk)
        except Homework.DoesNotExist:
            return None

    # ---------- GET BY ID ----------
    def get(self, request, pk):
        try:
            hw = self._get_object(pk)
            if hw is None:
                return Response(
                    {"success": False, "message": "Homework not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            return Response(
                {
                    "success": True,
                    "message": "Homework fetched successfully",
                    "data": HomeworkSerializer(hw).data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"success": False, "message": f"Server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # ---------- UPDATE ----------
    def put(self, request, pk):
        try:
            hw = self._get_object(pk)
            if hw is None:
                return Response(
                    {"success": False, "message": "Homework not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = HomeworkCreateUpdateSerializer(hw, data=request.data)
            if serializer.is_valid():
                hw = serializer.save()
                return Response(
                    {
                        "success": True,
                        "message": "Homework updated successfully",
                        "data": HomeworkSerializer(hw).data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {
                    "success": False,
                    "message": "Validation failed",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"success": False, "message": f"Server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # ---------- PARTIAL UPDATE ----------
    def patch(self, request, pk):
        try:
            hw = self._get_object(pk)
            if hw is None:
                return Response(
                    {"success": False, "message": "Homework not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = HomeworkCreateUpdateSerializer(
                hw, data=request.data, partial=True
            )
            if serializer.is_valid():
                hw = serializer.save()
                return Response(
                    {
                        "success": True,
                        "message": "Homework updated successfully",
                        "data": HomeworkSerializer(hw).data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {
                    "success": False,
                    "message": "Validation failed",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"success": False, "message": f"Server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # ---------- DELETE ----------
    def delete(self, request, pk):
        try:
            hw = self._get_object(pk)
            if hw is None:
                return Response(
                    {"success": False, "message": "Homework not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            hw.delete()
            return Response(
                {"success": True, "message": "Homework deleted successfully"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"success": False, "message": f"Server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )