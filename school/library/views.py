from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import LibraryBook
from .serializers import (
    LibraryBookSerializer,
    LibraryBookCreateUpdateSerializer,
)


# ==================== CREATE ====================
class LibraryCreateView(APIView):
    """
    POST /api/v1/school/library/create/
    Add a new book (multipart/form-data for images)
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = LibraryBookCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            book = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Book added successfully.",
                    "data": LibraryBookSerializer(book).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==================== LIST ====================
class LibraryListView(APIView):
    """
    GET /api/v1/school/library/list/
    Optional filters:
      ?class=Class 10
      ?subject=Maths
      ?search=sharma
    """
    def get(self, request):
        qs = LibraryBook.objects.all()

        book_class = request.query_params.get("class")
        subject = request.query_params.get("subject")
        search = request.query_params.get("search")

        if book_class and book_class != "All":
            qs = qs.filter(book_class=book_class)
        if subject and subject != "All":
            qs = qs.filter(subject=subject)
        if search:
            qs = qs.filter(author__icontains=search) | qs.filter(
                book_id__icontains=search
            )

        serializer = LibraryBookSerializer(qs, many=True)
        return Response(
            {
                "success": True,
                "count": qs.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ==================== DETAIL ====================
class LibraryDetailView(APIView):
    """
    GET    /api/v1/school/library/<id>/
    PUT    /api/v1/school/library/<id>/
    PATCH  /api/v1/school/library/<id>/
    DELETE /api/v1/school/library/<id>/
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return LibraryBook.objects.get(pk=pk)
        except LibraryBook.DoesNotExist:
            return None

    def get(self, request, pk):
        book = self.get_object(pk)
        if not book:
            return Response(
                {"success": False, "message": "Book not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"success": True, "data": LibraryBookSerializer(book).data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        book = self.get_object(pk)
        if not book:
            return Response(
                {"success": False, "message": "Book not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = LibraryBookCreateUpdateSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Book updated successfully.",
                    "data": LibraryBookSerializer(book).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        book = self.get_object(pk)
        if not book:
            return Response(
                {"success": False, "message": "Book not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = LibraryBookCreateUpdateSerializer(
            book, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Book updated successfully.",
                    "data": LibraryBookSerializer(book).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        book = self.get_object(pk)
        if not book:
            return Response(
                {"success": False, "message": "Book not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        book.delete()
        return Response(
            {"success": True, "message": "Book deleted successfully."},
            status=status.HTTP_200_OK,
        )