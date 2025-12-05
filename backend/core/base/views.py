"""
Base ViewSet for OurMES.

Provides a clean ViewSet base class without unnecessary boilerplate.
All ViewSets should inherit from this class.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.core.exceptions import ValidationError as DjangoValidationError

from .exceptions import DomainException, ValidationException, NotFoundException


class BaseViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet with common functionality for all endpoints.

    Features:
    - Automatic exception handling for domain exceptions
    - Clean interface without boilerplate perform_* methods
    - Consistent response formatting
    """

    def handle_exception(self, exc):
        """Convert domain exceptions to appropriate HTTP responses."""
        if isinstance(exc, NotFoundException):
            return Response(
                {'error': exc.message, 'code': exc.code},
                status=status.HTTP_404_NOT_FOUND
            )
        if isinstance(exc, ValidationException):
            error_data = {'error': exc.message, 'code': exc.code}
            if exc.field:
                error_data['field'] = exc.field
            return Response(error_data, status=status.HTTP_400_BAD_REQUEST)
        if isinstance(exc, DomainException):
            return Response(
                {'error': exc.message, 'code': exc.code},
                status=status.HTTP_400_BAD_REQUEST
            )
        if isinstance(exc, DjangoValidationError):
            return Response(
                {'error': str(exc), 'code': 'VALIDATION_ERROR'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().handle_exception(exc)

    def get_serializer_context(self):
        """Add request user to serializer context."""
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context


class ReadOnlyBaseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for endpoints that don't allow modifications.
    """

    def handle_exception(self, exc):
        """Convert domain exceptions to appropriate HTTP responses."""
        if isinstance(exc, NotFoundException):
            return Response(
                {'error': exc.message, 'code': exc.code},
                status=status.HTTP_404_NOT_FOUND
            )
        if isinstance(exc, DomainException):
            return Response(
                {'error': exc.message, 'code': exc.code},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().handle_exception(exc)
