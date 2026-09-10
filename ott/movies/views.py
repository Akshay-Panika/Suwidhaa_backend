from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Movie
from .serializers import MovieSerializer


class MovieListCreateAPIView(APIView):
    """
    GET: List all active movies
    POST: Create a new movie
    """
    def get(self, request):
        movies = Movie.objects.filter(is_active=True).order_by('-created_at')
        serializer = MovieSerializer(movies, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # content_type automatically "movie" set ho jayega
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
    DELETE: Soft delete a movie
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
        movie.is_active = False
        movie.save()
        return Response({
            "success": True,
            "message": "Movie deactivated successfully"
        }, status=status.HTTP_204_NO_CONTENT)