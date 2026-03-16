from rest_framework import serializers
from .models import Document, Field


class FieldSerializer(serializers.ModelSerializer):
    effective_value = serializers.CharField(read_only=True)

    class Meta:
        model = Field
        fields = [
            "id",
            "key",
            "original_value",
            "corrected_value",
            "effective_value",
            "data_type",
            "confidence",
            "corrected_at",
            "corrected_by",
        ]
        read_only_fields = [
            "id",
            "original_value",
            "data_type",
            "confidence",
            "corrected_at",
            "corrected_by",
        ]


class FieldCorrectionSerializer(serializers.ModelSerializer):
    """Used for PATCH /api/fields/{id}/ — only allows corrected_value."""

    class Meta:
        model = Field
        fields = ["corrected_value"]


class DocumentListSerializer(serializers.ModelSerializer):
    field_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "form_type",
            "original_filename",
            "content_type",
            "status",
            "uploaded_at",
            "field_count",
        ]


class DocumentDetailSerializer(serializers.ModelSerializer):
    fields = FieldSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "form_type",
            "original_filename",
            "content_type",
            "file_path",
            "status",
            "raw_text",
            "uploaded_at",
            "uploaded_by",
            "fields",
        ]


class DocumentUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    form_type = serializers.CharField(max_length=50)


class FieldIngestSerializer(serializers.Serializer):
    key = serializers.CharField(max_length=100)
    original_value = serializers.CharField()
    data_type = serializers.ChoiceField(
        choices=Field.DataType.choices, default="string"
    )
    confidence = serializers.FloatField(required=False, min_value=0.0, max_value=1.0)


class DocumentIngestSerializer(serializers.Serializer):
    form_type = serializers.CharField(max_length=50)
    original_filename = serializers.CharField(
        max_length=255, default="json_ingest.json"
    )
    fields = FieldIngestSerializer(many=True)
