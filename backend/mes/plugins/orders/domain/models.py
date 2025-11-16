from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from mes.plugins.basic.domain.models import Company, Product, ProductionLine
from mes.plugins.routing.domain.models import Technology


class Order(models.Model):
    """Production Order model"""
    STATE_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('declined', 'Declined'),
        ('interrupted', 'Interrupted'),
        ('abandoned', 'Abandoned'),
    ]

    number = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=1024)
    description = models.TextField(max_length=2048, blank=True)
    external_number = models.CharField(max_length=255, blank=True, unique=True, null=True)
    
    # Dates
    date_from = models.DateTimeField(null=True, blank=True)
    date_to = models.DateTimeField(null=True, blank=True)
    effective_date_from = models.DateTimeField(null=True, blank=True)
    effective_date_to = models.DateTimeField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    corrected_date_from = models.DateTimeField(null=True, blank=True)
    corrected_date_to = models.DateTimeField(null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    finish_date = models.DateTimeField(null=True, blank=True)
    
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='pending')
    
    # Relationships
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orders')
    technology = models.ForeignKey(Technology, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    production_line = models.ForeignKey(ProductionLine, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    # Quantities
    planned_quantity = models.DecimalField(
        max_digits=12, 
        decimal_places=5, 
        validators=[MinValueValidator(Decimal('0.00001'))]
    )
    done_quantity = models.DecimalField(
        max_digits=12, 
        decimal_places=5, 
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.number} - {self.name}"


class OrderStateChange(models.Model):
    """Order state change history"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='state_changes')
    source_state = models.CharField(max_length=20)
    target_state = models.CharField(max_length=20)
    date_and_time = models.DateTimeField(auto_now_add=True)
    worker = models.CharField(max_length=255, blank=True)
    
    class Meta:
        verbose_name = "Order State Change"
        verbose_name_plural = "Order State Changes"
        ordering = ['-date_and_time']

    def __str__(self):
        return f"{self.order.number}: {self.source_state} -> {self.target_state}"