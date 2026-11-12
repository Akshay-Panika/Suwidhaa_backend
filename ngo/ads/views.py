from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404

from .models import Ad
from .serializers import AdSerializer


class AdListCreateAPIView(APIView):
    """
    GET  : List ads (optional filters: ?is_active=true)
    POST : Create new ad (multipart form-data or JSON)
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        try:
            qs = Ad.objects.all()

            # Optional filter
            is_active = request.query_params.get("is_active")
            if is_active is not None:
                qs = qs.filter(is_active=is_active.lower() == "true")

            serializer = AdSerializer(qs, many=True)
            return Response(
                {
                    "success": True,
                    "count": qs.count(),
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
            serializer = AdSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "success": True,
                        "message": "Ad created successfully",
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


class AdDetailAPIView(APIView):
    """GET | PUT | DELETE — single ad"""
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        return get_object_or_404(Ad, pk=pk)

    def get(self, request, pk):
        try:
            ad = self.get_object(pk)
            serializer = AdSerializer(ad)
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Ad.DoesNotExist:
            return Response(
                {"success": False, "error": "Ad not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, pk):
        try:
            ad = self.get_object(pk)
            serializer = AdSerializer(ad, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "success": True,
                        "message": "Ad updated successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Ad.DoesNotExist:
            return Response(
                {"success": False, "error": "Ad not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, pk):
        try:
            ad = self.get_object(pk)
            ad.delete()
            return Response(
                {"success": True, "message": "Ad deleted successfully"},
                status=status.HTTP_200_OK,
            )
        except Ad.DoesNotExist:
            return Response(
                {"success": False, "error": "Ad not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )