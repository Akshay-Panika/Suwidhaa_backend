from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import ItServiceAd
from .serializers import ItServiceAdSerializer


class ItServiceAdCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = ItServiceAdSerializer(data=request.data)

        if serializer.is_valid():
            ad = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "IT service ad created successfully",
                    "data": ItServiceAdSerializer(ad).data,
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


class ItServiceAdListView(APIView):

    def get(self, request):
        ads = ItServiceAd.objects.all().order_by("-id")
        serializer = ItServiceAdSerializer(ads, many=True)

        return Response(
            {
                "success": True,
                "count": ads.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ItServiceAdDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return ItServiceAd.objects.get(pk=pk)
        except ItServiceAd.DoesNotExist:
            return None

    def get(self, request, pk):
        ad = self.get_object(pk)
        if not ad:
            return Response(
                {"success": False, "message": "IT service ad not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"success": True, "data": ItServiceAdSerializer(ad).data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        ad = self.get_object(pk)
        if not ad:
            return Response(
                {"success": False, "message": "IT service ad not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ItServiceAdSerializer(ad, data=request.data)

        if serializer.is_valid():
            ad = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "IT service ad updated successfully",
                    "data": ItServiceAdSerializer(ad).data,
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
        ad = self.get_object(pk)
        if not ad:
            return Response(
                {"success": False, "message": "IT service ad not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ItServiceAdSerializer(
            ad, data=request.data, partial=True
        )

        if serializer.is_valid():
            ad = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "IT service ad updated successfully",
                    "data": ItServiceAdSerializer(ad).data,
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
        ad = self.get_object(pk)
        if not ad:
            return Response(
                {"success": False, "message": "IT service ad not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        ad.delete()
        return Response(
            {
                "success": True,
                "message": "IT service ad deleted successfully",
            },
            status=status.HTTP_200_OK,
        )