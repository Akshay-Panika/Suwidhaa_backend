from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import CollegeBanner
from .serializers import CollegeBannerSerializer


class CollegeBannerCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = CollegeBannerSerializer(data=request.data)

        if serializer.is_valid():
            banner = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "College banner created successfully",
                    "data": CollegeBannerSerializer(banner).data,
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


class CollegeBannerListView(APIView):

    def get(self, request):
        banners = CollegeBanner.objects.all().order_by("-id")
        serializer = CollegeBannerSerializer(banners, many=True)

        return Response(
            {
                "success": True,
                "count": banners.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class CollegeBannerDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return CollegeBanner.objects.get(pk=pk)
        except CollegeBanner.DoesNotExist:
            return None

    def get(self, request, pk):
        banner = self.get_object(pk)

        if not banner:
            return Response(
                {
                    "success": False,
                    "message": "College banner not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "success": True,
                "data": CollegeBannerSerializer(banner).data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        banner = self.get_object(pk)

        if not banner:
            return Response(
                {
                    "success": False,
                    "message": "College banner not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CollegeBannerSerializer(
            banner,
            data=request.data
        )

        if serializer.is_valid():
            banner = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "College banner updated successfully",
                    "data": CollegeBannerSerializer(banner).data,
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
                    "message": "College banner not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CollegeBannerSerializer(
            banner,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            banner = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "College banner updated successfully",
                    "data": CollegeBannerSerializer(banner).data,
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
                    "message": "College banner not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        banner.delete()

        return Response(
            {
                "success": True,
                "message": "College banner deleted successfully",
            },
            status=status.HTTP_200_OK,
        )