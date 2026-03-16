import json
import os

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render

from .models import Document, Field
from .services import extract_text_from_pdf, parse_fields_from_text


# Full pages
def index(request):
    recent_docs = Document.objects.all()[:10]
    return render(request, "documents/index.html", {"documents": recent_docs})


def document_detail(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)
    return render(request, "documents/detail.html", {"document": document})


def upload_page(request):
    return render(request, "documents/upload.html")


def register_page(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")
    else:
        form = UserCreationForm()
    return render(request, "documents/register.html", {"form": form})


# HTMX partials — uploads
@login_required
def upload_pdf(request):
    if request.method != "POST":
        return render(
            request,
            "documents/partials/upload_result.html",
            {"error": "Invalid method"},
        )

    uploaded_file = request.FILES.get("file")
    form_type = request.POST.get("form_type", "").strip()

    if not uploaded_file or not form_type:
        return render(
            request,
            "documents/partials/upload_result.html",
            {"error": "Both a PDF file and form type are required."},
        )

    # Save file
    upload_dir = os.path.join(settings.MEDIA_ROOT, "documents")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)

    doc = Document.objects.create(
        form_type=form_type,
        original_filename=uploaded_file.name,
        content_type=uploaded_file.content_type or "application/pdf",
        file_path=file_path,
        status=Document.Status.PROCESSING,
        uploaded_by=request.user,
    )

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
    return render(request, "documents/partials/upload_result.html", {"document": doc})


@login_required
def upload_json(request):
    if request.method != "POST":
        return render(
            request,
            "documents/partials/upload_result.html",
            {"error": "Invalid method"},
        )

    raw_body = request.POST.get("json_body", "").strip()
    form_type = request.POST.get("form_type", "").strip()

    if not raw_body or not form_type:
        return render(
            request,
            "documents/partials/upload_result.html",
            {"error": "Both JSON body and form type are required."},
        )

    try:
        data = json.loads(raw_body)
    except json.JSONDecodeError as e:
        return render(
            request,
            "documents/partials/upload_result.html",
            {"error": f"Invalid JSON: {e}"},
        )

    fields_data = data.get("fields", [])
    original_filename = data.get("original_filename", "json_ingest.json")

    doc = Document.objects.create(
        form_type=form_type,
        original_filename=original_filename,
        content_type="application/json",
        status=Document.Status.PROCESSED,
        uploaded_by=request.user,
    )

    for field_data in fields_data:
        Field.objects.create(
            document=doc,
            key=field_data.get("key", ""),
            original_value=field_data.get("original_value", ""),
            data_type=field_data.get("data_type", "string"),
            confidence=field_data.get("confidence"),
        )

    return render(request, "documents/partials/upload_result.html", {"document": doc})
