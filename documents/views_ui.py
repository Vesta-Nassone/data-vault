import json

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render

from .models import Document, Field


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
