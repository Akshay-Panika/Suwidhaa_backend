from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import College, CollegeImage
from .serializers import CollegeSerializer

class CollegeCreateView(APIView):
    """Create a new college with images"""
    
    def post(self, request):
        # Create college
        college = College.objects.create(
            name=request.data.get('name'),
            address=request.data.get('address'),
            website=request.data.get('website', '')
        )
        
        # Handle multiple images manually
        images = request.FILES.getlist('images')
        for image in images:
            CollegeImage.objects.create(
                college=college,
                image=image
            )
        
        serializer = CollegeSerializer(college)
        return Response({
            "success": True,
            "message": "College created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


class CollegeListView(APIView):
    """List all colleges"""
    
    def get(self, request):
        colleges = College.objects.all().order_by('-id')
        serializer = CollegeSerializer(colleges, many=True)
        return Response({
            "success": True,
            "count": colleges.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class CollegeDetailView(APIView):
    """Get, update, delete a specific college"""
    
    def get_object(self, pk):
        try:
            return College.objects.get(pk=pk)
        except College.DoesNotExist:
            return None
    
    def get(self, request, pk):
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
    
    def put(self, request, pk):
        college = self.get_object(pk)
        if not college:
            return Response({
                "success": False,
                "message": "College not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Update fields manually
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
    
    def delete(self, request, pk):
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