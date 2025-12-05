"""
Base models for OurMES.

Provides common functionality for all domain models including:
- Automatic timestamp tracking (created_at, updated_at)
- Soft delete capability
- Common model methods
"""
from django.db import models


class TimestampedModel(models.Model):
    """
    Abstract base model that provides automatic timestamp tracking.

    All domain models should inherit from this class to ensure
    consistent timestamp behavior across the application.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteManager(models.Manager):
    """Manager that filters out soft-deleted records by default."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def with_deleted(self):
        """Include soft-deleted records in queryset."""
        return super().get_queryset()

    def deleted_only(self):
        """Return only soft-deleted records."""
        return super().get_queryset().filter(is_deleted=True)


class SoftDeleteModel(TimestampedModel):
    """
    Abstract model that provides soft delete functionality.

    Records are not actually deleted from the database but marked
    as deleted with a timestamp.
    """
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, hard=False):
        """
        Soft delete the record by default.
        Pass hard=True to permanently delete.
        """
        if hard:
            return super().delete(using=using, keep_parents=keep_parents)

        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])
