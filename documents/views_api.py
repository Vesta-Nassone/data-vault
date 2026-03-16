import os
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import DocumentFilter
from .models import Document, Field
from .serializers import (
    DocumentDetailSerializer,
    DocumentIngestSerializer,
    DocumentListSerializer,
    DocumentUploadSerializer,
    FieldCorrectionSerializer,
    FieldSerializer,
)
from .services import extract_text_from_pdf, parse_fields_from_text


# Auth
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email", "")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "username and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "username already taken"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "username": user.username},
            status=status.HTTP_201_CREATED,
        )


# Documents
class DocumentListView(generics.ListAPIView):
    serializer_class = DocumentListSerializer
    filterset_class = DocumentFilter

    def get_queryset(self):
        return Document.objects.annotate(field_count=Count("fields"))


class DocumentDetailView(generics.RetrieveAPIView):
    queryset = Document.objects.prefetch_related("fields")
    serializer_class = DocumentDetailSerializer
    lookup_field = "pk"


class DocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DocumentUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = serializer.validated_data["file"]
        form_type = serializer.validated_data["form_type"]

        # Save file
        upload_dir = os.path.join(settings.MEDIA_ROOT, "documents")
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        # Create document record
        doc = Document.objects.create(
            form_type=form_type,
            original_filename=uploaded_file.name,
            content_type=uploaded_file.content_type or "application/pdf",
            file_path=file_path,
            status=Document.Status.PROCESSING,
            uploaded_by=request.user,
        )

        # Extract fields
        try:
            raw_text = extract_text_from_pdf(file_path)
            doc.raw_text = raw_text
            parsed = parse_fields_from_text(raw_text)
            for field_data in parsed:
                Field.objects.create(document=doc, **field_data)
            doc.status = Document.Status.PROCESSED
        except Exception as e:
            doc.status = Document.Status.ERROR
            doc.raw_text = str(e)

        doc.save()
        return Response(
            DocumentDetailSerializer(doc).data, status=status.HTTP_201_CREATED
        )


class DocumentIngestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DocumentIngestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        doc = Document.objects.create(
            form_type=data["form_type"],
            original_filename=data["original_filename"],
            content_type="application/json",
            status=Document.Status.PROCESSED,
            uploaded_by=request.user,
        )

        for field_data in data["fields"]:
            Field.objects.create(
                document=doc,
                key=field_data["key"],
                original_value=field_data["original_value"],
                data_type=field_data.get("data_type", "string"),
                confidence=field_data.get("confidence"),
            )

        return Response(
            DocumentDetailSerializer(doc).data, status=status.HTTP_201_CREATED
        )


# Fields
class FieldCorrectionView(generics.UpdateAPIView):
    queryset = Field.objects.all()
    serializer_class = FieldCorrectionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"
    http_method_names = ["patch"]

    def perform_update(self, serializer):
        serializer.save(
            corrected_at=timezone.now(),
            corrected_by=self.request.user,
        )

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # Return full field representation
        return Response(FieldSerializer(instance).data)


# Reports
class TopCorrectionsView(APIView):
    def get(self, request):
        results = (
            Field.objects.filter(corrected_value__isnull=False)
            .values("key")
            .annotate(correction_count=Count("id"))
            .order_by("-correction_count")[:3]
        )
        return Response(list(results))


class DocumentsByTypeView(APIView):
    def get(self, request):
        qs = Document.objects.all()
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")
        if date_from:
            qs = qs.filter(uploaded_at__gte=date_from)
        if date_to:
            qs = qs.filter(uploaded_at__lte=date_to)
        results = (
            qs.values("form_type")
            .annotate(doc_count=Count("id"))
            .order_by("-doc_count")
        )
        return Response(list(results))
