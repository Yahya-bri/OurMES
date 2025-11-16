from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from mes.plugins.basic.domain.models import Product, Workstation


class Technology(models.Model):
    """Technology model representing production processes"""
    STATE_CHOICES = [
        ('draft', 'Draft'),
        ('accepted', 'Accepted'),
        ('checked', 'Checked'),
        ('outdated', 'Outdated'),
        ('declined', 'Declined'),
    ]

    number = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=1024)
    description = models.TextField(max_length=2048, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='technologies')
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='draft')
    master = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Technology"
        verbose_name_plural = "Technologies"
        ordering = ['number']

    def __str__(self):
        return f"{self.number} - {self.name}"


class Operation(models.Model):
    """Operation model representing single production step"""
    number = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=1024)
    description = models.TextField(blank=True)
    
    # Time parameters (in seconds)
    tj = models.IntegerField(default=0, help_text="Time for batch (seconds)")
    tpz = models.IntegerField(default=0, help_text="Preparation time (seconds)")
    time_next_operation = models.IntegerField(default=0, help_text="Time to next operation (seconds)")
    
    workstations = models.ManyToManyField(Workstation, related_name='operations', blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Operation"
        verbose_name_plural = "Operations"
        ordering = ['number']

    def __str__(self):
        return f"{self.number} - {self.name}"


class TechnologyOperationComponent(models.Model):
    """Links operations to technologies in a tree structure"""
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE, related_name='operation_components')
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE, related_name='technology_components')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    
    node_number = models.CharField(max_length=255)
    priority = models.IntegerField(default=1)
    
    # Time overrides
    tj = models.IntegerField(null=True, blank=True, help_text="Override time for batch")
    tpz = models.IntegerField(null=True, blank=True, help_text="Override preparation time")
    time_next_operation = models.IntegerField(null=True, blank=True, help_text="Override time to next operation")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Technology Operation Component"
        verbose_name_plural = "Technology Operation Components"
        ordering = ['technology', 'node_number']

    def __str__(self):
        return f"{self.technology.number} - {self.operation.number}"


class OperationProductInComponent(models.Model):
    """Input products for operations"""
    operation_component = models.ForeignKey(
        TechnologyOperationComponent, 
        on_delete=models.CASCADE, 
        related_name='input_products'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='operation_inputs')
    quantity = models.DecimalField(
        max_digits=12, 
        decimal_places=5,
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    class Meta:
        verbose_name = "Operation Product In Component"
        verbose_name_plural = "Operation Product In Components"

    def __str__(self):
        return f"{self.product.number} ({self.quantity})"


class OperationProductOutComponent(models.Model):
    """Output products for operations"""
    operation_component = models.ForeignKey(
        TechnologyOperationComponent, 
        on_delete=models.CASCADE, 
        related_name='output_products'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='operation_outputs')
    quantity = models.DecimalField(
        max_digits=12, 
        decimal_places=5,
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    class Meta:
        verbose_name = "Operation Product Out Component"
        verbose_name_plural = "Operation Product Out Components"

    def __str__(self):
        return f"{self.product.number} ({self.quantity})"