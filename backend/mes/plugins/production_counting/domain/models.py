from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator
from mes.plugins.orders.domain.models import Order
from mes.plugins.basic.domain.models import Product, Workstation, Staff
from mes.plugins.routing.domain.models import Operation, TechnologyOperationComponent


class ProductionCounting(models.Model):
    """Production progress registration granular per operation component.
    Represents quantity produced (done) at a given point in time for one operation
    of an order's technology. Aggregations will derive overall progress.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='production_counts')
    operation = models.ForeignKey(Operation, on_delete=models.SET_NULL, null=True, blank=True, related_name='production_counts')
    component = models.ForeignKey(TechnologyOperationComponent, on_delete=models.SET_NULL, null=True, blank=True, related_name='production_counts')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='production_counts')
    workstation = models.ForeignKey(Workstation, on_delete=models.SET_NULL, null=True, blank=True, related_name='production_counts')
    # quantities
    done_quantity = models.DecimalField(max_digits=12, decimal_places=5, default=Decimal('0'), validators=[MinValueValidator(Decimal('0'))])
    rejected_quantity = models.DecimalField(max_digits=12, decimal_places=5, default=Decimal('0'), validators=[MinValueValidator(Decimal('0'))])
    # execution tracking
    operator = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='production_counts')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('in_progress','in_progress'), ('completed','completed')], default='in_progress')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Production Counting"
        verbose_name_plural = "Production Countings"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.order.number} - {self.operation.number if self.operation_id else 'N/A'} - {self.done_quantity}"

    @property
    def net_quantity(self):
        return self.done_quantity - self.rejected_quantity