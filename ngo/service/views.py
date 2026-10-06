from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import NgoService
from .serializers import NgoServiceSerializer


class NgoServiceCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = NgoServiceSerializer(data=request.data)

        if serializer.is_valid():
            service = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "NGO service created successfully",
                    "data": NgoServiceSerializer(service).data,
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


class NgoServiceListView(APIView):

    def get(self, request):
        services = NgoService.objects.all().order_by("-id")
        serializer = NgoServiceSerializer(services, many=True)

        return Response(
            {
                "success": True,
                "count": services.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class NgoServiceDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return NgoService.objects.get(pk=pk)
        except NgoService.DoesNotExist:
            return None

    def get(self, request, pk):
        service = self.get_object(pk)

        if not service:
            return Response(
                {
                    "success": False,
                    "message": "NGO service not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "success": True,
                "data": NgoServiceSerializer(service).data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        service = self.get_object(pk)

        if not service:
            return Response(
                {
                    "success": False,
                    "message": "NGO service not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = NgoServiceSerializer(
            service,
            data=request.data,
        )

        if serializer.is_valid():
            service = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "NGO service updated successfully",
                    "data": NgoServiceSerializer(service).data,
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

    def patch(self, request, pk):
        service = self.get_object(pk)

        if not service:
            return Response(
                {
                    "success": False,
                    "message": "NGO service not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = NgoServiceSerializer(
            service,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            service = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "NGO service updated successfully",
                    "data": NgoServiceSerializer(service).data,
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

    def delete(self, request, pk):
        service = self.get_object(pk)

        if not service:
            return Response(
                {
                    "success": False,
                    "message": "NGO service not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        service.delete()

        return Response(
            {
                "success": True,
                "message": "NGO service deleted successfully",
            },
            status=status.HTTP_200_OK,
        )