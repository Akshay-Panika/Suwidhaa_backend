from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Movie
from .serializers import MovieSerializer


class MovieCreateView(APIView):

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = MovieSerializer(data=request.data)

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
                "message": "Movie creation failed",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
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

        if movie is None:
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

        if movie is None:
            return Response(
                {
                    "success": False,
                    "message": "Movie not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = MovieSerializer(
            movie,
            data=request.data
        )

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
                "message": "Movie update failed",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        movie = self.get_object(pk)

        if movie is None:
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