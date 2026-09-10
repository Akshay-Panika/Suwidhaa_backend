from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Movie
from .serializers import MovieSerializer


class MovieListCreateAPIView(APIView):
    """
    GET: List all movies (active + inactive)
    POST: Create a new movie
    """
    def get(self, request):
        movies = Movie.objects.all().order_by('-created_at')  # filter hata diya
        serializer = MovieSerializer(movies, many=True)
        return Response({
            "success": True,
            "count": movies.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Movie created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class MovieDetailAPIView(APIView):
    """
    GET: Retrieve a single movie
    PUT: Update a movie
    DELETE: Hard delete a movie
    """
    def get_object(self, pk):
        return get_object_or_404(Movie, pk=pk)

    def get(self, request, pk):
        movie = self.get_object(pk)
        serializer = MovieSerializer(movie)
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, pk):
        movie = self.get_object(pk)
        serializer = MovieSerializer(movie, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Movie updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        movie = self.get_object(pk)
        movie.delete()   # hard delete (database se hamesha ke liye hata dega)
        return Response({
            "success": True,
            "message": "Movie deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)