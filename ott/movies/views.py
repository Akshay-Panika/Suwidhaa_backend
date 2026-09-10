from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Movie
from .serializers import MovieSerializer


class MovieListCreateAPIView(APIView):
    """GET: List all movies | POST: Create a new movie"""

    def get(self, request):
        try:
            movies = Movie.objects.all().order_by('-created_at')
            serializer = MovieSerializer(movies, many=True)
            return Response({
                "success": True,
                "count": movies.count(),
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
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
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MovieDetailAPIView(APIView):
    """GET | PUT | DELETE a single movie"""

    def get_object(self, pk):
        return get_object_or_404(Movie, pk=pk)

    def get(self, request, pk):
        try:
            movie = self.get_object(pk)
            serializer = MovieSerializer(movie)
            return Response({
                "success": True,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Movie.DoesNotExist:
            return Response({
                "success": False,
                "error": "Movie not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
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
        except Movie.DoesNotExist:
            return Response({
                "success": False,
                "error": "Movie not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        try:
            movie = self.get_object(pk)
            title = movie.title
            movie.delete()   # Cascade delete → Content bhi delete ho jayega
            return Response({
                "success": True,
                "message": f"Movie '{title}' deleted successfully"
            }, status=status.HTTP_200_OK)   # ← 200 use karo taaki body aaye
        except Movie.DoesNotExist:
            return Response({
                "success": False,
                "error": "Movie not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)