from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import models
from .models import College, CollegeImage
from .serializers import CollegeSerializer

class CollegeCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        # Get data
        name = request.data.get('name')
        address = request.data.get('address')
        website = request.data.get('website', '')
        contact_number = request.data.get('contact_number', '')
        category = request.data.get('category', '')
        is_recommended = request.data.get('is_recommended', 'false').lower() == 'true'
        logo = request.FILES.get('logo')
        
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
            contact_number=contact_number,
            category=category,
            is_recommended=is_recommended
        )
        
        # Handle logo
        if logo:
            college.logo = logo
            college.save()
        
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
        # Get filters from query params
        category = request.query_params.get('category')
        is_recommended = request.query_params.get('is_recommended')
        search = request.query_params.get('search')
        
        # Start with all colleges
        colleges = College.objects.all().order_by('-id')
        
        # Filter by category if provided
        if category:
            colleges = colleges.filter(category__icontains=category)
        
        # Filter by is_recommended if provided
        if is_recommended is not None:
            is_recommended_bool = is_recommended.lower() == 'true'
            colleges = colleges.filter(is_recommended=is_recommended_bool)
        
        # Search by name or address
        if search:
            colleges = colleges.filter(
                models.Q(name__icontains=search) | 
                models.Q(address__icontains=search)
            )
        
        serializer = CollegeSerializer(colleges, many=True)
        return Response({
            "success": True,
            "count": colleges.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class CollegeDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    
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
        college.contact_number = request.data.get('contact_number', college.contact_number)
        college.category = request.data.get('category', college.category)
        
        # Update is_recommended if provided
        if request.data.get('is_recommended') is not None:
            college.is_recommended = request.data.get('is_recommended', 'false').lower() == 'true'
        
        # Handle logo update
        logo = request.FILES.get('logo')
        if logo:
            college.logo = logo
        
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