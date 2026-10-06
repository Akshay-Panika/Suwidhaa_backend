from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import NgoBanner
from .serializers import NgoBannerSerializer


class NgoBannerCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = NgoBannerSerializer(data=request.data)

        if serializer.is_valid():
            banner = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "NGO banner created successfully",
                    "data": NgoBannerSerializer(banner).data,
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


class NgoBannerListView(APIView):

    def get(self, request):
        banners = NgoBanner.objects.all().order_by("-id")
        serializer = NgoBannerSerializer(banners, many=True)

        return Response(
            {
                "success": True,
                "count": banners.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class NgoBannerDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return NgoBanner.objects.get(pk=pk)
        except NgoBanner.DoesNotExist:
            return None

    def get(self, request, pk):
        banner = self.get_object(pk)

        if not banner:
            return Response(
                {
                    "success": False,
                    "message": "NGO banner not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "success": True,
                "data": NgoBannerSerializer(banner).data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        banner = self.get_object(pk)

        if not banner:
            return Response(
                {
                    "success": False,
                    "message": "NGO banner not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = NgoBannerSerializer(
            banner,
            data=request.data,
        )

        if serializer.is_valid():
            banner = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "NGO banner updated successfully",
                    "data": NgoBannerSerializer(banner).data,
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
                {
                    "success": False,
                    "message": "NGO banner not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = NgoBannerSerializer(
            banner,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            banner = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "NGO banner updated successfully",
                    "data": NgoBannerSerializer(banner).data,
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
                {
                    "success": False,
                    "message": "NGO banner not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        banner.delete()

        return Response(
            {
                "success": True,
                "message": "NGO banner deleted successfully",
            },
            status=status.HTTP_200_OK,
        )