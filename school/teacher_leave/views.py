from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import TeacherLeave
from .serializers import TeacherLeaveSerializer


class TeacherLeaveCreateView(APIView):

    def post(self, request):
        serializer = TeacherLeaveSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": True, "message": "Leave applied successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"status": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class TeacherLeaveListView(APIView):

    def get(self, request):
        leaves = TeacherLeave.objects.all()
        serializer = TeacherLeaveSerializer(leaves, many=True)
        return Response(
            {"status": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class TeacherLeaveDetailView(APIView):

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
        serializer = TeacherLeaveSerializer(leave)
        return Response(
            {"status": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        leave = self.get_object(pk)
        if not leave:
            return Response(
                {"status": False, "message": "Leave not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = TeacherLeaveSerializer(leave, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": True, "message": "Leave updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"status": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        leave = self.get_object(pk)
        if not leave:
            return Response(
                {"status": False, "message": "Leave not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = TeacherLeaveSerializer(leave, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": True, "message": "Leave updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"status": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

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


class TeacherLeaveByIdCardView(APIView):

    def get(self, request, teacher_id_card):
        leaves = TeacherLeave.objects.filter(teacher_id_card=teacher_id_card)
        if not leaves.exists():
            return Response(
                {"status": False, "message": "No leaves found for this teacher id card"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = TeacherLeaveSerializer(leaves, many=True)
        return Response(
            {"status": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )