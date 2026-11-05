from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Movie
from .serializers import MovieSerializer
from ott.category.models import Category   # adjust to your app path


class MovieListCreateAPIView(APIView):
    """
    GET  /movies/list/                → All Content (virtual id=0)
    GET  /movies/list/?category=0     → All Content
    GET  /movies/list/?category=3     → Only category 3
    POST /movies/create/              → category required (real id > 0)
    """

    def get(self, request):
        try:
            category_raw = request.query_params.get("category")

            qs = Movie.objects.select_related("category").order_by("-created_at")

            if category_raw is not None and category_raw != "":
                try:
                    cid = int(category_raw)
                except (TypeError, ValueError):
                    return Response(
                        {"success": False, "error": "Invalid category id"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if cid > 0:
                    if not Category.objects.filter(pk=cid).exists():
                        return Response(
                            {"success": False, "error": f"Category {cid} not found"},
                            status=status.HTTP_404_NOT_FOUND,
                        )
                    qs = qs.filter(category_id=cid)
                # cid == 0 → All Content (no filter)

            serializer = MovieSerializer(qs, many=True)
            return Response(
                {
                    "success": True,
                    "count": qs.count(),
                    "category": category_raw,
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        try:
            serializer = MovieSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "success": True,
                        "message": "Movie created successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MovieDetailAPIView(APIView):
    """GET | PUT | DELETE a single movie"""

    def get_object(self, pk):
        return get_object_or_404(Movie, pk=pk)

    def get(self, request, pk):
        try:
            movie = self.get_object(pk)
            serializer = MovieSerializer(movie)
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Movie.DoesNotExist:
            return Response(
                {"success": False, "error": "Movie not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, pk):
        try:
            movie = self.get_object(pk)
            serializer = MovieSerializer(movie, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "success": True,
                        "message": "Movie updated successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Movie.DoesNotExist:
            return Response(
                {"success": False, "error": "Movie not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, pk):
        try:
            movie = self.get_object(pk)
            title = movie.title
            movie.delete()   # Cascade → Content auto-deleted
            return Response(
                {"success": True, "message": f"Movie '{title}' deleted successfully"},
                status=status.HTTP_200_OK,
            )
        except Movie.DoesNotExist:
            return Response(
                {"success": False, "error": "Movie not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )