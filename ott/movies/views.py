import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Movie
from .serializers import MovieSerializer
import cloudinary.uploader

logger = logging.getLogger(__name__)

class MovieCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            data = request.data.copy()
            
            # Handle horizontal thumbnail
            if 'thumbnail_horizontal' in request.FILES:
                result = cloudinary.uploader.upload(
                    request.FILES['thumbnail_horizontal'],
                    folder="suwidhaa/ott/movies/horizontal"
                )
                data['thumbnail_horizontal'] = result['secure_url']
            
            # Handle vertical thumbnail
            if 'thumbnail_vertical' in request.FILES:
                result = cloudinary.uploader.upload(
                    request.FILES['thumbnail_vertical'],
                    folder="suwidhaa/ott/movies/vertical"
                )
                data['thumbnail_vertical'] = result['secure_url']
            
            serializer = MovieSerializer(data=data)
            if serializer.is_valid():
                movie = serializer.save()
                return Response(
                    {
                        "success": True,
                        "message": "Movie created successfully",
                        "data": MovieSerializer(movie).data
                    },
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {
                    "success": False,
                    "message": "Validation failed",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MovieListView(APIView):
    def get(self, request):
        movies = Movie.objects.all().order_by("-created_at")
        serializer = MovieSerializer(movies, many=True)
        return Response(
            {
                "success": True,
                "message": "Movies fetched successfully",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )


class MovieDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, pk):
        try:
            return Movie.objects.get(pk=pk)
        except Movie.DoesNotExist:
            return None

    def get(self, request, pk):
        movie = self.get_object(pk)
        if not movie:
            return Response(
                {
                    "success": False,
                    "message": "Movie not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = MovieSerializer(movie)
        return Response(
            {
                "success": True,
                "message": "Movie fetched successfully",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def put(self, request, pk):
        movie = self.get_object(pk)
        if not movie:
            return Response(
                {
                    "success": False,
                    "message": "Movie not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        data = request.data.copy()
        
        # Handle horizontal thumbnail upload
        if 'thumbnail_horizontal' in request.FILES:
            result = cloudinary.uploader.upload(
                request.FILES['thumbnail_horizontal'],
                folder="suwidhaa/ott/movies/horizontal"
            )
            data['thumbnail_horizontal'] = result['secure_url']
        
        # Handle vertical thumbnail upload
        if 'thumbnail_vertical' in request.FILES:
            result = cloudinary.uploader.upload(
                request.FILES['thumbnail_vertical'],
                folder="suwidhaa/ott/movies/vertical"
            )
            data['thumbnail_vertical'] = result['secure_url']
        
        serializer = MovieSerializer(movie, data=data, partial=True)
        if serializer.is_valid():
            movie = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Movie updated successfully",
                    "data": MovieSerializer(movie).data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "success": False,
                "message": "Validation failed",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        movie = self.get_object(pk)
        if not movie:
            return Response(
                {
                    "success": False,
                    "message": "Movie not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        movie.delete()
        return Response(
            {
                "success": True,
                "message": "Movie deleted successfully"
            },
            status=status.HTTP_200_OK
        )