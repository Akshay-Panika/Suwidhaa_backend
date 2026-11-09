from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404

from .models import Content
from .serializers import ContentSerializer


class ContentListCreateAPIView(APIView):
    """
    GET  : List content (optional filter: ?category_id=3)
    POST : Create new content (multipart form-data ya JSON)
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        try:
            qs = Content.objects.select_related("category").all()

            # ── Filter by category (id=0 ya missing → sab kuch) ──
            category_id = request.query_params.get("category_id")
            if category_id and category_id not in ("0", ""):
                qs = qs.filter(category_id=category_id)

            serializer = ContentSerializer(qs, many=True)
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
            serializer = ContentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "success": True,
                        "message": "Content created successfully",
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


class ContentDetailAPIView(APIView):
    """GET | PUT | DELETE a single content by id"""
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        return get_object_or_404(Content, pk=pk)

    def get(self, request, pk):
        try:
            content = self.get_object(pk)
            serializer = ContentSerializer(content)
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Content.DoesNotExist:
            return Response(
                {"success": False, "error": "Content not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, pk):
        try:
            content = self.get_object(pk)
            serializer = ContentSerializer(
                content, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "success": True,
                        "message": "Content updated successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Content.DoesNotExist:
            return Response(
                {"success": False, "error": "Content not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, pk):
        try:
            content = self.get_object(pk)
            content.delete()
            return Response(
                {"success": True, "message": "Content deleted successfully"},
                status=status.HTTP_200_OK,
            )
        except Content.DoesNotExist:
            return Response(
                {"success": False, "error": "Content not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )