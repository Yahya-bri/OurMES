"""
Query utilities for optimized database operations.

Provides helper functions for common query patterns.
"""
from django.db.models import Count, Q


def get_stats_aggregation(queryset, state_field='state', state_choices=None):
    """
    Get aggregated statistics for a queryset with state field.

    Uses a single database query with conditional aggregation
    instead of multiple separate queries.

    Args:
        queryset: The base queryset to aggregate
        state_field: Name of the state field
        state_choices: List of (value, label) tuples for states

    Returns:
        Dict with total count and counts per state
    """
    aggregations = {'total': Count('id')}

    if state_choices:
        for state_value, _ in state_choices:
            aggregations[state_value] = Count(
                'id',
                filter=Q(**{state_field: state_value})
            )

    return queryset.aggregate(**aggregations)


def prefetch_for_list(queryset, *related_fields):
    """
    Apply select_related and prefetch_related for list views.

    Optimizes queries by eager loading related objects.
    """
    fk_fields = []
    m2m_fields = []

    for field in related_fields:
        if '__' in field or hasattr(queryset.model, field):
            # Assume FK/OneToOne for dotted paths
            fk_fields.append(field)
        else:
            m2m_fields.append(field)

    if fk_fields:
        queryset = queryset.select_related(*fk_fields)
    if m2m_fields:
        queryset = queryset.prefetch_related(*m2m_fields)

    return queryset
