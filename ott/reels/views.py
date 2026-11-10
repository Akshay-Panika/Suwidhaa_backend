from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Reel
from .serializers import ReelSerializer


class ReelListAPIView(APIView):
    """
    GET -> Saare reels ki list return karega
    """

    def get(self, request):
        reels = Reel.objects.all().order_by('-created_at')
        serializer = ReelSerializer(reels, many=True)
        return Response(
            {
                "status": True,
                "message": "Reels fetched successfully",
                "count": reels.count(),
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

class ReelDetailAPIView(APIView):
    """
    GET    /api/v1/ott/reels/<pk>/  → Single reel detail
    PUT    /api/v1/ott/reels/<pk>/  → Update reel
    PATCH  /api/v1/ott/reels/<pk>/  → Partial update
    DELETE /api/v1/ott/reels/<pk>/  → Delete reel
    """

    def get_object(self, pk):
        try:
            return Reel.objects.get(pk=pk)
        except Reel.DoesNotExist:
            return None

    # ── SHOW ──
    def get(self, request, pk):
        reel = self.get_object(pk)
        if not reel:
            return Response(
                {"status": False, "message": "Reel not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            {
                "status": True,
                "message": "Reel fetched successfully",
                "data": ReelSerializer(reel).data
            },
            status=status.HTTP_200_OK
        )

    # ── UPDATE ──
    def put(self, request, pk):
        return self._update(request, pk, partial=False)

    def patch(self, request, pk):
        return self._update(request, pk, partial=True)

    def _update(self, request, pk, partial):
        reel = self.get_object(pk)
        if not reel:
            return Response(
                {"status": False, "message": "Reel not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ReelSerializer(reel, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "Reel updated successfully",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "status": False,
                "message": "Invalid data",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # ── DELETE ──
    def delete(self, request, pk):
        reel = self.get_object(pk)
        if not reel:
            return Response(
                {"status": False, "message": "Reel not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        reel.delete()
        return Response(
            {"status": True, "message": "Reel deleted successfully"},
            status=status.HTTP_200_OK
        )

class ReelCreateAPIView(APIView):
    """
    POST -> Naya reel create karega
    """

    def post(self, request):
        # Empty body check
        if not request.data:
            return Response(
                {
                    "status": False,
                    "message": "Request body empty hai, data bhejiye"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ReelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "Reel created successfully",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                "status": False,
                "message": "Invalid data",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )