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