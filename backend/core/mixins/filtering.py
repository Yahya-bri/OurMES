"""
Filtering mixins for ViewSets.

Provides common filtering patterns for list views.
"""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


class FilteringMixin:
    """
    Mixin providing standard filtering capabilities.

    Includes:
    - Django filter backend for field filtering
    - Search filter for text search
    - Ordering filter for sorting

    Usage:
        class MyViewSet(FilteringMixin, BaseViewSet):
            filterset_fields = ['status', 'category']
            search_fields = ['name', 'description']
            ordering_fields = ['created_at', 'name']
    """
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = []
    search_fields = []
    ordering_fields = []
    ordering = ['-created_at']


class DateRangeFilterMixin:
    """
    Mixin for filtering by date ranges.

    Expects query parameters:
    - date_from: Start date (inclusive)
    - date_to: End date (inclusive)
    """
    date_field = 'created_at'

    def get_queryset(self):
        queryset = super().get_queryset()

        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')

        if date_from:
            queryset = queryset.filter(**{f'{self.date_field}__gte': date_from})
        if date_to:
            queryset = queryset.filter(**{f'{self.date_field}__lte': date_to})

        return queryset
