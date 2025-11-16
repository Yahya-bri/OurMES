from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator
from mes.plugins.orders.domain.models import Order
from mes.plugins.routing.domain.models import TechnologyOperationComponent


class Scheduling(models.Model):
    """Simple schedule record for an order operation component.
    Provides computed start/end times and duration estimates.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='schedule_items')
    component = models.ForeignKey(TechnologyOperationComponent, on_delete=models.CASCADE, related_name='schedule_items')
    sequence_index = models.PositiveIntegerField(default=0)
    planned_start = models.DateTimeField()
    planned_end = models.DateTimeField()
    duration_seconds = models.PositiveIntegerField()
    buffer_seconds = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    locked = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Schedule Item"
        verbose_name_plural = "Schedule Items"
        ordering = ['order', 'sequence_index']

    def __str__(self):
        return f"{self.order.number} - {self.component.node_number}"