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
            # Log incoming data for debugging
            print("=== REQUEST DATA ===")
            print("Data:", request.data)
            print("FILES:", request.FILES)
            print("====================")
            
            # Create a mutable copy of request data
            data = request.data.copy()
            
            # Handle thumbnail_horizontal upload
            if 'thumbnail_horizontal' in request.FILES:
                try:
                    uploaded_file = request.FILES['thumbnail_horizontal']
                    result = cloudinary.uploader.upload(
                        uploaded_file,
                        folder="suwidhaa/ott/movies/horizontal"
                    )
                    data['thumbnail_horizontal'] = result['secure_url']
                    print(f"Horizontal uploaded: {result['secure_url']}")
                except Exception as e:
                    print(f"Horizontal upload error: {str(e)}")
                    return Response(
                        {
                            "success": False,
                            "message": f"Horizontal thumbnail upload failed: {str(e)}"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                # If no file, set to None
                data['thumbnail_horizontal'] = None
                print("No horizontal file provided")
            
            # Handle thumbnail_vertical upload
            if 'thumbnail_vertical' in request.FILES:
                try:
                    uploaded_file = request.FILES['thumbnail_vertical']
                    result = cloudinary.uploader.upload(
                        uploaded_file,
                        folder="suwidhaa/ott/movies/vertical"
                    )
                    data['thumbnail_vertical'] = result['secure_url']
                    print(f"Vertical uploaded: {result['secure_url']}")
                except Exception as e:
                    print(f"Vertical upload error: {str(e)}")
                    return Response(
                        {
                            "success": False,
                            "message": f"Vertical thumbnail upload failed: {str(e)}"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                data['thumbnail_vertical'] = None
                print("No vertical file provided")
            
            # Log processed data
            print("=== PROCESSED DATA ===")
            print(data)
            print("======================")
            
            # Create serializer with processed data
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
            else:
                print("=== SERIALIZER ERRORS ===")
                print(serializer.errors)
                print("==========================")
                return Response(
                    {
                        "success": False,
                        "message": "Movie creation failed",
                        "errors": serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            import traceback
            print("=== EXCEPTION ===")
            print(traceback.format_exc())
            print("=================")
            return Response(
                {
                    "success": False,
                    "message": f"An error occurred: {str(e)}",
                    "traceback": traceback.format_exc()  # Remove this in production
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
        
        data = request.data.copy()
        
        # Handle file uploads for update
        if 'thumbnail_horizontal' in request.FILES:
            try:
                result = cloudinary.uploader.upload(
                    request.FILES['thumbnail_horizontal'],
                    folder="suwidhaa/ott/movies/horizontal"
                )
                data['thumbnail_horizontal'] = result['secure_url']
            except Exception as e:
                return Response(
                    {
                        "success": False,
                        "message": f"Horizontal thumbnail upload failed: {str(e)}"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if 'thumbnail_vertical' in request.FILES:
            try:
                result = cloudinary.uploader.upload(
                    request.FILES['thumbnail_vertical'],
                    folder="suwidhaa/ott/movies/vertical"
                )
                data['thumbnail_vertical'] = result['secure_url']
            except Exception as e:
                return Response(
                    {
                        "success": False,
                        "message": f"Vertical thumbnail upload failed: {str(e)}"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = MovieSerializer(movie, data=data)
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