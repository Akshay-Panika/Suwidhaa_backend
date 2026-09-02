from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import College, CollegeImage
from .serializers import CollegeSerializer

class CollegeCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        # Get data
        name = request.data.get('name')
        address = request.data.get('address')
        website = request.data.get('website', '')
        category = request.data.get('category', '')  # Free text, can be anything
        
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
        
        # Create college
        college = College.objects.create(
            name=name,
            address=address,
            website=website,
            category=category  # User can enter anything
        )
        
        # Handle images
        images = request.FILES.getlist('images')
        for image in images:
            CollegeImage.objects.create(
                college=college,
                image=image
            )
        
        # Return response
        serializer = CollegeSerializer(college)
        return Response({
            "success": True,
            "message": "College created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


class CollegeListView(APIView):
    def get(self, request):
        # Get category filter from query params
        category = request.query_params.get('category')
        
        # Filter by category if provided (exact match)
        if category:
            colleges = College.objects.filter(category__icontains=category).order_by('-id')
        else:
            colleges = College.objects.all().order_by('-id')
        
        serializer = CollegeSerializer(colleges, many=True)
        return Response({
            "success": True,
            "count": colleges.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class CollegeDetailView(APIView):
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
        
        # Update fields
        college.name = request.data.get('name', college.name)
        college.address = request.data.get('address', college.address)
        college.website = request.data.get('website', college.website)
        college.category = request.data.get('category', college.category)  # Free text
        
        college.save()
        
        # Handle images (replace all old images with new ones)
        images = request.FILES.getlist('images')
        if images:
            college.images.all().delete()
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