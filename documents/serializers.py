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
