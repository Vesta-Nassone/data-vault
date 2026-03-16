import django_filters
from django.db import models
from django.db.models import FloatField
from django.db.models.functions import Cast
from .models import Document


class DocumentFilter(django_filters.FilterSet):
    form_type = django_filters.CharFilter(field_name="form_type", lookup_expr="exact")
    uploaded_after = django_filters.DateTimeFilter(
        field_name="uploaded_at", lookup_expr="gte"
    )
    uploaded_before = django_filters.DateTimeFilter(
        field_name="uploaded_at", lookup_expr="lte"
    )
    field_key = django_filters.CharFilter(method="filter_by_field_key")
    field_value = django_filters.CharFilter(method="filter_by_field_value")
    amount_min = django_filters.NumberFilter(method="filter_amount_min")
    amount_max = django_filters.NumberFilter(method="filter_amount_max")

    class Meta:
        model = Document
        fields = []

    def filter_by_field_key(self, queryset, name, value):
        return queryset.filter(fields__key=value).distinct()

    def filter_by_field_value(self, queryset, name, value):
        return queryset.filter(
            models.Q(fields__original_value__icontains=value)
            | models.Q(fields__corrected_value__icontains=value)
        ).distinct()

    def filter_amount_min(self, queryset, name, value):
        return (
            queryset.filter(
                fields__key="amount",
                fields__data_type="number",
            )
            .annotate(amount_val=Cast("fields__original_value", FloatField()))
            .filter(amount_val__gte=value)
            .distinct()
        )

    def filter_amount_max(self, queryset, name, value):
        return (
            queryset.filter(
                fields__key="amount",
                fields__data_type="number",
            )
            .annotate(amount_val=Cast("fields__original_value", FloatField()))
            .filter(amount_val__lte=value)
            .distinct()
        )
