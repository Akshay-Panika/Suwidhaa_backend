from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Cartoon
from .serializers import CartoonSerializer


class CartoonListCreateAPIView(APIView):
    """GET: List all cartoons | POST: Create a new cartoon"""

    def get(self, request):
        try:
            cartoons = Cartoon.objects.all().order_by('-created_at')
            serializer = CartoonSerializer(cartoons, many=True)
            return Response({
                "success": True,
                "count": cartoons.count(),
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = CartoonSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Cartoon created successfully",
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


class CartoonDetailAPIView(APIView):
    """GET | PUT | DELETE a single cartoon"""

    def get_object(self, pk):
        return get_object_or_404(Cartoon, pk=pk)

    def get(self, request, pk):
        try:
            cartoon = self.get_object(pk)
            serializer = CartoonSerializer(cartoon)
            return Response({
                "success": True,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Cartoon.DoesNotExist:
            return Response({
                "success": False,
                "error": "Cartoon not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            cartoon = self.get_object(pk)
            serializer = CartoonSerializer(cartoon, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "message": "Cartoon updated successfully",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Cartoon.DoesNotExist:
            return Response({
                "success": False,
                "error": "Cartoon not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        try:
            cartoon = self.get_object(pk)
            title = cartoon.title
            cartoon.delete()   # Cascade delete → Content bhi delete
            return Response({
                "success": True,
                "message": f"Cartoon '{title}' deleted successfully"
            }, status=status.HTTP_200_OK)
        except Cartoon.DoesNotExist:
            return Response({
                "success": False,
                "error": "Cartoon not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)