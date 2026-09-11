from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Reel
from .serializers import ReelSerializer


class ReelListCreateAPIView(APIView):
    """
    GET  -> Saare reels ki list return karega
    POST -> Naya reel create karega
    """

    def get(self, request):
        reels = Reel.objects.all().order_by('-created_at')
        serializer = ReelSerializer(reels, many=True)
        return Response(
            {
                "status": True,
                "message": "Reels fetched successfully",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
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


class ReelDetailAPIView(APIView):
    """
    GET    -> Ek specific reel ki detail
    PUT    -> Reel update karega
    DELETE -> Reel delete karega
    """

    def get_object(self, pk):
        try:
            return Reel.objects.get(pk=pk)
        except Reel.DoesNotExist:
            return None

    def get(self, request, pk):
        reel = self.get_object(pk)
        if not reel:
            return Response(
                {"status": False, "message": "Reel not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ReelSerializer(reel)
        return Response(
            {"status": True, "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def put(self, request, pk):
        reel = self.get_object(pk)
        if not reel:
            return Response(
                {"status": False, "message": "Reel not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ReelSerializer(reel, data=request.data)
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
            {"status": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

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
            status=status.HTTP_204_NO_CONTENT
        )