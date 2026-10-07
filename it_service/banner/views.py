from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import ItServiceBanner
from .serializers import ItServiceBannerSerializer


class ItServiceBannerCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = ItServiceBannerSerializer(data=request.data)

        if serializer.is_valid():
            banner = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "IT service banner created successfully",
                    "data": ItServiceBannerSerializer(banner).data,
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


class ItServiceBannerListView(APIView):

    def get(self, request):
        banners = ItServiceBanner.objects.all().order_by("-id")
        serializer = ItServiceBannerSerializer(banners, many=True)

        return Response(
            {
                "success": True,
                "count": banners.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ItServiceBannerDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return ItServiceBanner.objects.get(pk=pk)
        except ItServiceBanner.DoesNotExist:
            return None

    def get(self, request, pk):
        banner = self.get_object(pk)
        if not banner:
            return Response(
                {"success": False, "message": "IT service banner not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"success": True, "data": ItServiceBannerSerializer(banner).data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        banner = self.get_object(pk)
        if not banner:
            return Response(
                {"success": False, "message": "IT service banner not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ItServiceBannerSerializer(banner, data=request.data)

        if serializer.is_valid():
            banner = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "IT service banner updated successfully",
                    "data": ItServiceBannerSerializer(banner).data,
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
        banner = self.get_object(pk)
        if not banner:
            return Response(
                {"success": False, "message": "IT service banner not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ItServiceBannerSerializer(
            banner, data=request.data, partial=True
        )

        if serializer.is_valid():
            banner = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "IT service banner updated successfully",
                    "data": ItServiceBannerSerializer(banner).data,
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
        banner = self.get_object(pk)
        if not banner:
            return Response(
                {"success": False, "message": "IT service banner not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        banner.delete()
        return Response(
            {
                "success": True,
                "message": "IT service banner deleted successfully",
            },
            status=status.HTTP_200_OK,
        )