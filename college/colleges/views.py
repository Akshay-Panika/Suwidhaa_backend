from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
from .models import College, CollegeImage
from .serializers import CollegeSerializer

logger = logging.getLogger(__name__)

class CollegeCreateView(APIView):
    def post(self, request):
        try:
            # Log everything
            print("=== REQUEST DATA ===")
            print(request.data)
            print(request.FILES)
            print(request.POST)
            
            # Get data
            name = request.data.get('name')
            address = request.data.get('address')
            website = request.data.get('website', '')
            
            # Validate
            if not name:
                return Response({
                    "success": False,
                    "message": "Name is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not address:
                return Response({
                    "success": False,
                    "message": "Address is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create college (no images first)
            college = College.objects.create(
                name=name,
                address=address,
                website=website
            )
            
            # Try to handle images
            images = request.FILES.getlist('images')
            
            if images:
                for image in images:
                    try:
                        # Print image info
                        print(f"Image: {image.name}, Size: {image.size}, Type: {image.content_type}")
                        
                        # Try to create CollegeImage
                        college_image = CollegeImage.objects.create(
                            college=college,
                            image=image
                        )
                        print(f"Created CollegeImage ID: {college_image.id}")
                        
                    except Exception as e:
                        print(f"Error creating image: {str(e)}")
                        # Continue with other images
            else:
                print("No images provided")
            
            serializer = CollegeSerializer(college)
            return Response({
                "success": True,
                "message": "College created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"=== ERROR ===")
            print(str(e))
            import traceback
            traceback.print_exc()
            
            return Response({
                "success": False,
                "message": str(e),
                "error_type": type(e).__name__
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class CollegeListView(APIView):
    """List all colleges"""
    
    def get(self, request):
        try:
            colleges = College.objects.all().order_by('-id')
            serializer = CollegeSerializer(colleges, many=True)
            return Response({
                "success": True,
                "count": colleges.count(),
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching colleges: {str(e)}")
            return Response({
                "success": False,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CollegeDetailView(APIView):
    """Get, update, delete a specific college"""
    
    def get_object(self, pk):
        try:
            return College.objects.get(pk=pk)
        except College.DoesNotExist:
            return None
    
    def get(self, request, pk):
        try:
            college = self.get_object(pk)
            if not college:
                return Response({
                    "success": False,
                    "message": "College not found"
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = CollegeSerializer(college)
            return Response({
                "success": True,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching college: {str(e)}")
            return Response({
                "success": False,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request, pk):
        try:
            college = self.get_object(pk)
            if not college:
                return Response({
                    "success": False,
                    "message": "College not found"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Update fields
            college.name = request.data.get('name', college.name)
            college.address = request.data.get('address', college.address)
            college.website = request.data.get('website', college.website)
            college.save()
            
            # Handle new images if provided
            images = request.FILES.getlist('images')
            if images:
                # Delete old images
                college.images.all().delete()
                # Add new images
                for image in images:
                    CollegeImage.objects.create(
                        college=college,
                        image=image
                    )
            
            serializer = CollegeSerializer(college)
            return Response({
                "success": True,
                "message": "College updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error updating college: {str(e)}")
            return Response({
                "success": False,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, pk):
        try:
            college = self.get_object(pk)
            if not college:
                return Response({
                    "success": False,
                    "message": "College not found"
                }, status=status.HTTP_404_NOT_FOUND)
            
            college.delete()
            return Response({
                "success": True,
                "message": "College deleted successfully"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error deleting college: {str(e)}")
            return Response({
                "success": False,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)