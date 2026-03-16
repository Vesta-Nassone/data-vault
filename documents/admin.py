from django.contrib import admin
from .models import Document, Field


class FieldInline(admin.TabularInline):
    model = Field
    extra = 0
    readonly_fields = ("id", "corrected_at", "corrected_by")


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "form_type",
        "original_filename",
        "status",
        "uploaded_at",
        "uploaded_by",
    )
    list_filter = ("form_type", "status")
    search_fields = ("original_filename", "form_type")
    readonly_fields = ("id", "uploaded_at")
    inlines = [FieldInline]


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = (
        "key",
        "document",
        "original_value",
        "corrected_value",
        "data_type",
        "confidence",
    )
    list_filter = ("data_type", "key")
    search_fields = ("key", "original_value", "corrected_value")
    readonly_fields = ("id", "corrected_at", "corrected_by")
