from django.urls import path
from django.contrib.auth import views as auth_views
from . import views_ui

urlpatterns = [
    # Full pages
    path("", views_ui.index, name="index"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="documents/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    path("register/", views_ui.register_page, name="register"),
    path("upload/", views_ui.upload_page, name="upload"),
    path("documents/<uuid:doc_id>/", views_ui.document_detail, name="document-detail"),
    path("search/", views_ui.search_page, name="search"),
    # HTMX partials
    path("upload/pdf/", views_ui.upload_pdf, name="upload-pdf"),
    path("upload/json/", views_ui.upload_json, name="upload-json"),
    path("fields/<uuid:field_id>/edit/", views_ui.field_edit_form, name="field-edit"),
    path(
        "fields/<uuid:field_id>/correct/", views_ui.field_correct, name="field-correct"
    ),
    path("fields/<uuid:field_id>/row/", views_ui.field_row, name="field-row"),
    path("search/results/", views_ui.search_results, name="search-results"),
]
