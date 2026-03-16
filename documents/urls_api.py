from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views_api

urlpatterns = [
    # Auth
    path("auth/register/", views_api.RegisterView.as_view(), name="api-register"),
    path("auth/token/", obtain_auth_token, name="api-token"),
    # Documents
    path("documents/", views_api.DocumentListView.as_view(), name="api-document-list"),
    path(
        "documents/upload/",
        views_api.DocumentUploadView.as_view(),
        name="api-document-upload",
    ),
    path(
        "documents/ingest/",
        views_api.DocumentIngestView.as_view(),
        name="api-document-ingest",
    ),
    path(
        "documents/<uuid:pk>/",
        views_api.DocumentDetailView.as_view(),
        name="api-document-detail",
    ),
    # Fields
    path(
        "fields/<uuid:pk>/",
        views_api.FieldCorrectionView.as_view(),
        name="api-field-correct",
    ),
    # Reports
    path(
        "reports/top-corrections/",
        views_api.TopCorrectionsView.as_view(),
        name="api-top-corrections",
    ),
    path(
        "reports/documents-by-type/",
        views_api.DocumentsByTypeView.as_view(),
        name="api-docs-by-type",
    ),
]
