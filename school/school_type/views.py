from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import SchoolType
from .serializers import SchoolTypeSerializer


class SchoolTypeCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        school_code = request.data.get("school_code")

        if school_code and SchoolType.objects.filter(school_code=school_code).exists():
            return Response(
                {"success": False, "message": f"School code '{school_code}' already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SchoolTypeSerializer(data=request.data)

        if serializer.is_valid():
            school = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "School created successfully",
                    "data": SchoolTypeSerializer(school).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class SchoolTypeListView(APIView):
    def get(self, request):
        schools = SchoolType.objects.all()
        serializer = SchoolTypeSerializer(schools, many=True)

        return Response(
            {
                "success": True,
                "count": schools.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class SchoolTypeDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return SchoolType.objects.get(pk=pk)
        except SchoolType.DoesNotExist:
            return None

    def get(self, request, pk):
        school = self.get_object(pk)
        if not school:
            return Response(
                {"success": False, "message": "School not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"success": True, "data": SchoolTypeSerializer(school).data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        school = self.get_object(pk)
        if not school:
            return Response(
                {"success": False, "message": "School not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if "school_code" in request.data:
            new_code = request.data.get("school_code")
            if SchoolType.objects.filter(school_code=new_code).exclude(id=pk).exists():
                return Response(
                    {"success": False, "message": f"School code '{new_code}' already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = SchoolTypeSerializer(school, data=request.data)
        if serializer.is_valid():
            school = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "School updated successfully",
                    "data": SchoolTypeSerializer(school).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        school = self.get_object(pk)
        if not school:
            return Response(
                {"success": False, "message": "School not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if "school_code" in request.data:
            new_code = request.data.get("school_code")
            if SchoolType.objects.filter(school_code=new_code).exclude(id=pk).exists():
                return Response(
                    {"success": False, "message": f"School code '{new_code}' already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = SchoolTypeSerializer(school, data=request.data, partial=True)
        if serializer.is_valid():
            school = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "School updated successfully",
                    "data": SchoolTypeSerializer(school).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        school = self.get_object(pk)
        if not school:
            return Response(
                {"success": False, "message": "School not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        school.delete()
        return Response(
            {"success": True, "message": "School deleted successfully"},
            status=status.HTTP_200_OK,
        )