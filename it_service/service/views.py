from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import ItServiceService
from .serializers import ItServiceServiceSerializer


class ItServiceServiceCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = ItServiceServiceSerializer(data=request.data)

        if serializer.is_valid():
            service = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "IT service created successfully",
                    "data": ItServiceServiceSerializer(service).data,
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


class ItServiceServiceListView(APIView):

    def get(self, request):
        services = ItServiceService.objects.all().order_by("-id")

        # Optional filter: ?category=<id>
        category_id = request.query_params.get("category")
        if category_id:
            services = services.filter(category_id=category_id)

        serializer = ItServiceServiceSerializer(services, many=True)

        return Response(
            {
                "success": True,
                "count": services.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ItServiceServiceDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return ItServiceService.objects.get(pk=pk)
        except ItServiceService.DoesNotExist:
            return None

    def get(self, request, pk):
        service = self.get_object(pk)
        if not service:
            return Response(
                {"success": False, "message": "IT service not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"success": True, "data": ItServiceServiceSerializer(service).data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        service = self.get_object(pk)
        if not service:
            return Response(
                {"success": False, "message": "IT service not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ItServiceServiceSerializer(service, data=request.data)

        if serializer.is_valid():
            service = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "IT service updated successfully",
                    "data": ItServiceServiceSerializer(service).data,
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
                {"success": False, "message": "IT service not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ItServiceServiceSerializer(
            service, data=request.data, partial=True
        )

        if serializer.is_valid():
            service = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "IT service updated successfully",
                    "data": ItServiceServiceSerializer(service).data,
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
                {"success": False, "message": "IT service not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        service.delete()
        return Response(
            {
                "success": True,
                "message": "IT service deleted successfully",
            },
            status=status.HTTP_200_OK,
        )