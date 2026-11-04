from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import TeacherLeave
from .serializers import TeacherLeaveSerializer


# ═══════════════════════════════════════════════════════════
# CREATE
#   POST /teacher-leave/create/
#   Returns full teacher + school in response
# ═══════════════════════════════════════════════════════════
class TeacherLeaveCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = TeacherLeaveSerializer(data=request.data)
        if serializer.is_valid():
            leave = serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "Leave applied successfully",
                    "data": TeacherLeaveSerializer(leave).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"status": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


# ═══════════════════════════════════════════════════════════
# LIST ALL
#   GET /teacher-leave/list/
# ═══════════════════════════════════════════════════════════
class TeacherLeaveListView(APIView):
    def get(self, request):
        leaves = TeacherLeave.objects.all()
        serializer = TeacherLeaveSerializer(leaves, many=True)
        return Response(
            {
                "status": True,
                "count": leaves.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ═══════════════════════════════════════════════════════════
# DETAIL / UPDATE / DELETE
#   GET/PUT/PATCH/DELETE /teacher-leave/<pk>/
# ═══════════════════════════════════════════════════════════
class TeacherLeaveDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return TeacherLeave.objects.get(pk=pk)
        except TeacherLeave.DoesNotExist:
            return None

    def get(self, request, pk):
        leave = self.get_object(pk)
        if not leave:
            return Response(
                {"status": False, "message": "Leave not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"status": True, "data": TeacherLeaveSerializer(leave).data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        leave = self.get_object(pk)
        if not leave:
            return Response(
                {"status": False, "message": "Leave not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = TeacherLeaveSerializer(
            leave, data=request.data, partial=True
        )
        if serializer.is_valid():
            leave = serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "Leave updated",
                    "data": TeacherLeaveSerializer(leave).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"status": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        return self.put(request, pk)

    def delete(self, request, pk):
        leave = self.get_object(pk)
        if not leave:
            return Response(
                {"status": False, "message": "Leave not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        leave.delete()
        return Response(
            {"status": True, "message": "Leave deleted successfully"},
            status=status.HTTP_200_OK,
        )


# ═══════════════════════════════════════════════════════════
# TEACHER-WISE LIST (by id_card)
#   GET /teacher-leave/list/<teacher_id_card>/
# ═══════════════════════════════════════════════════════════
class TeacherLeaveByIdCardView(APIView):
    def get(self, request, teacher_id_card):
        leaves = TeacherLeave.objects.filter(
            teacher_id_card=str(teacher_id_card).strip()
        ).order_by("-created_date")

        if not leaves.exists():
            return Response(
                {
                    "status": True,
                    "count": 0,
                    "teacher_id_card": teacher_id_card,
                    "data": [],
                },
                status=status.HTTP_200_OK,
            )

        serializer = TeacherLeaveSerializer(leaves, many=True)
        return Response(
            {
                "status": True,
                "count": leaves.count(),
                "teacher_id_card": teacher_id_card,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ═══════════════════════════════════════════════════════════
# ✅ NEW: TEACHER-WISE LIST (by DB integer id)
#   GET /teacher-leave/teacher/<teacher_id>/
# ═══════════════════════════════════════════════════════════
class TeacherLeaveByTeacherIdView(APIView):
    def get(self, request, teacher_id):
        target = str(teacher_id).strip()
        leaves = TeacherLeave.objects.filter(
            teacher_id=target
        ).order_by("-created_date")

        if not leaves.exists():
            return Response(
                {
                    "status": True,
                    "count": 0,
                    "teacher_id": teacher_id,
                    "data": [],
                },
                status=status.HTTP_200_OK,
            )

        serializer = TeacherLeaveSerializer(leaves, many=True)
        return Response(
            {
                "status": True,
                "count": leaves.count(),
                "teacher_id": teacher_id,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ═══════════════════════════════════════════════════════════
# ✅ NEW: SCHOOL-WISE LIST
#   GET /teacher-leave/school/<school_id>/
#   (filters leaves whose teacher belongs to that school)
# ═══════════════════════════════════════════════════════════
class TeacherLeaveBySchoolView(APIView):
    def get(self, request, school_id):
        try:
            from school.teacher.models import Teacher
        except Exception:
            return Response(
                {"status": False, "message": "Teacher model unavailable"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Get all teacher_id_cards for this school
        teacher_cards = list(
            Teacher.objects.filter(school_id=school_id)
            .values_list("teacher_id_card", flat=True)
        )

        if not teacher_cards:
            return Response(
                {
                    "status": True,
                    "count": 0,
                    "school_id": school_id,
                    "data": [],
                },
                status=status.HTTP_200_OK,
            )

        leaves = TeacherLeave.objects.filter(
            teacher_id_card__in=teacher_cards
        ).order_by("-created_date")

        serializer = TeacherLeaveSerializer(leaves, many=True)
        return Response(
            {
                "status": True,
                "count": leaves.count(),
                "school_id": school_id,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )