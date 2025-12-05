"""
Bulk action mixins for ViewSets.

Provides reusable bulk operations that can be added to any ViewSet.
"""
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response


class BulkActionsMixin:
    """
    Mixin providing bulk CRUD operations for ViewSets.

    Requires the ViewSet to have a `service` attribute pointing
    to a service class with bulk methods.

    Usage:
        class MyViewSet(BulkActionsMixin, BaseViewSet):
            service = MyService
    """
    service = None

    def get_service(self):
        """Get the service class for this ViewSet."""
        if self.service is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} must define a 'service' attribute"
            )
        return self.service

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """Delete multiple records by IDs."""
        ids = request.data.get('ids', [])
        if not ids:
            return Response(
                {'error': 'No ids provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        deleted_count = self.get_service().bulk_delete(ids)
        return Response({
            'status': 'success',
            'deleted_count': deleted_count
        })

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Update multiple records with the same data."""
        ids = request.data.get('ids', [])
        data = request.data.get('data', {})

        if not ids:
            return Response(
                {'error': 'No ids provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not data:
            return Response(
                {'error': 'No data provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_count = self.get_service().bulk_update(ids, **data)
        return Response({
            'status': 'success',
            'updated_count': updated_count
        })


class BulkStateMixin:
    """
    Mixin for bulk state change operations.

    Requires the ViewSet to have a `service` attribute pointing
    to a StatefulService subclass.
    """
    service = None

    @action(detail=False, methods=['post'])
    def bulk_change_state(self, request):
        """Change state for multiple records."""
        ids = request.data.get('ids', [])
        new_state = request.data.get('state')

        if not ids:
            return Response(
                {'error': 'No ids provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not new_state:
            return Response(
                {'error': 'No state provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            updated_count = self.service.bulk_change_state(ids, new_state)
        except Exception as exc:
            return Response(
                {'error': str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'status': 'success',
            'updated_count': updated_count,
            'new_state': new_state
        })
