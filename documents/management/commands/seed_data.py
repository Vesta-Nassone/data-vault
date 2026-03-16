"""
Management command to seed test data for development/demo.

Usage:
    python manage.py seed_data
    python manage.py seed_data --clear   # clears existing data first
    
NOTE: I used AI to mock up realistic document and field data, including common form types.
"""

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from documents.models import Document, Field


SEED_DOCUMENTS = [
    {
        "form_type": "w9",
        "original_filename": "w9_acme_corp.pdf",
        "content_type": "application/pdf",
        "status": "processed",
        "fields": [
            {
                "key": "customer_name",
                "original_value": "Acme Corporation",
                "data_type": "string",
                "confidence": 0.95,
            },
            {
                "key": "ein",
                "original_value": "12-3456789",
                "data_type": "string",
                "confidence": 0.88,
            },
            {
                "key": "address",
                "original_value": "123 Main St, Springfield, IL 62701",
                "data_type": "string",
                "confidence": 0.75,
            },
            {
                "key": "date",
                "original_value": "01/15/2026",
                "data_type": "date",
                "confidence": 0.90,
            },
        ],
        "corrections": {},
    },
    {
        "form_type": "ach_authorization",
        "original_filename": "ach_auth_smith.pdf",
        "content_type": "application/pdf",
        "status": "processed",
        "fields": [
            {
                "key": "customer_name",
                "original_value": "John Smithh",
                "data_type": "string",
                "confidence": 0.82,
            },
            {
                "key": "account_number",
                "original_value": "9876543210",
                "data_type": "string",
                "confidence": 0.91,
            },
            {
                "key": "routing_number",
                "original_value": "021000021",
                "data_type": "string",
                "confidence": 0.94,
            },
            {
                "key": "amount",
                "original_value": "2500.00",
                "data_type": "number",
                "confidence": 0.88,
            },
        ],
        # customer_name has typo — will be corrected
        "corrections": {"customer_name": "John Smith"},
    },
    {
        "form_type": "loan_application",
        "original_filename": "loan_app_jones.json",
        "content_type": "application/json",
        "status": "processed",
        "fields": [
            {
                "key": "customer_name",
                "original_value": "Sarah Jomes",
                "data_type": "string",
                "confidence": 0.78,
            },
            {
                "key": "amount",
                "original_value": "50000.00",
                "data_type": "number",
                "confidence": 0.96,
            },
            {
                "key": "date",
                "original_value": "03/01/2026",
                "data_type": "date",
                "confidence": 0.93,
            },
            {
                "key": "email",
                "original_value": "sarah.jones@example.com",
                "data_type": "string",
                "confidence": 0.99,
            },
            {
                "key": "ssn",
                "original_value": "123-45-6789",
                "data_type": "string",
                "confidence": 0.85,
            },
        ],
        # customer_name has typo — will be corrected
        "corrections": {"customer_name": "Sarah Jones"},
    },
    {
        "form_type": "w9",
        "original_filename": "w9_globex.json",
        "content_type": "application/json",
        "status": "processed",
        "fields": [
            {
                "key": "customer_name",
                "original_value": "Globex Corporation",
                "data_type": "string",
                "confidence": 0.97,
            },
            {
                "key": "ein",
                "original_value": "98-7654321",
                "data_type": "string",
                "confidence": 0.92,
            },
            {
                "key": "address",
                "original_value": "742 Evergreen Terrace, Springfield, IL",
                "data_type": "string",
                "confidence": 0.80,
            },
            {
                "key": "amount",
                "original_value": "125000.00",
                "data_type": "number",
                "confidence": 0.91,
            },
        ],
        "corrections": {},
    },
    {
        "form_type": "ach_authorization",
        "original_filename": "ach_auth_williams.json",
        "content_type": "application/json",
        "status": "processed",
        "fields": [
            {
                "key": "customer_name",
                "original_value": "Robert Willliams",
                "data_type": "string",
                "confidence": 0.79,
            },
            {
                "key": "account_number",
                "original_value": "1234567890",
                "data_type": "string",
                "confidence": 0.95,
            },
            {
                "key": "routing_number",
                "original_value": "121000358",
                "data_type": "string",
                "confidence": 0.97,
            },
            {
                "key": "amount",
                "original_value": "750.00",
                "data_type": "number",
                "confidence": 0.89,
            },
            {
                "key": "date",
                "original_value": "02/28/2026",
                "data_type": "date",
                "confidence": 0.94,
            },
        ],
        # customer_name has typo — will be corrected
        "corrections": {"customer_name": "Robert Williams"},
    },
]


class Command(BaseCommand):
    help = "Seed the database with test documents and fields."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing documents and fields before seeding.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            count = Document.objects.count()
            Document.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f"Cleared {count} existing documents.")
            )

        # Get or create a demo user for uploads
        demo_user, created = User.objects.get_or_create(
            username="demo",
            defaults={"email": "demo@datavault.local"},
        )
        if created:
            demo_user.set_password("demo1234")
            demo_user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    "Created demo user (username=demo, password=demo1234)"
                )
            )

        # Get or create a reviewer user for corrections
        reviewer, created = User.objects.get_or_create(
            username="reviewer",
            defaults={"email": "reviewer@datavault.local"},
        )
        if created:
            reviewer.set_password("review1234")
            reviewer.save()
            self.stdout.write(
                self.style.SUCCESS(
                    "Created reviewer user (username=reviewer, password=review1234)"
                )
            )

        for doc_data in SEED_DOCUMENTS:
            doc = Document.objects.create(
                form_type=doc_data["form_type"],
                original_filename=doc_data["original_filename"],
                content_type=doc_data["content_type"],
                status=doc_data["status"],
                uploaded_by=demo_user,
            )

            corrections = doc_data.get("corrections", {})
            for field_data in doc_data["fields"]:
                field = Field.objects.create(
                    document=doc,
                    key=field_data["key"],
                    original_value=field_data["original_value"],
                    data_type=field_data["data_type"],
                    confidence=field_data.get("confidence"),
                )
                if field_data["key"] in corrections:
                    field.corrected_value = corrections[field_data["key"]]
                    field.corrected_at = timezone.now()
                    field.corrected_by = reviewer
                    field.save()

            self.stdout.write(
                f"  Created: [{doc.form_type}] {doc.original_filename} ({doc.fields.count()} fields)"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSeeded {len(SEED_DOCUMENTS)} documents successfully."
            )
        )
        self.stdout.write("Demo credentials:")
        self.stdout.write("  uploader:  username=demo,     password=demo1234")
        self.stdout.write("  reviewer:  username=reviewer, password=review1234")
