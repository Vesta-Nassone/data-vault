import uuid
from django.db import models
from django.conf import settings


class Document(models.Model):
    class Status(models.TextChoices):
        UPLOADED = "uploaded"
        PROCESSING = "processing"
        PROCESSED = "processed"
        ERROR = "error"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form_type = models.CharField(max_length=50, db_index=True)
    original_filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.UPLOADED, db_index=True
    )
    raw_text = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, db_index=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="documents",
    )

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.form_type} — {self.original_filename}"