from django.db import models
from mes.plugins.basic.domain.models import Product
from mes.plugins.routing.domain.models import Operation


class InspectionConfig(models.Model):
    CHECK_TYPES = [
        ('pass_fail', 'Pass/Fail'),
        ('variable', 'Variable Data'),
    ]

    operation = models.ForeignKey(
        Operation, on_delete=models.CASCADE, related_name='inspection_configs')
    check_type = models.CharField(max_length=20, choices=CHECK_TYPES)
    description = models.CharField(max_length=255)
    parameters = models.CharField(
        max_length=255, blank=True)  # e.g., "10.0 +/- 0.1"
    mandatory = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.operation.name} - {self.description}"


class QualityCheck(models.Model):
    config = models.ForeignKey(InspectionConfig, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=100)
    # "Pass", "Fail", or numeric value
    result_value = models.CharField(max_length=100)
    passed = models.BooleanField()
    inspector_name = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order_number} - {self.config.description}: {self.result_value}"


class NCR(models.Model):
    STATUS_CHOICES = [
        ('quarantine', 'Quarantine'),
        ('review', 'Review'),
        ('closed', 'Closed'),
    ]

    ncr_number = models.CharField(max_length=100, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    issue_description = models.TextField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='quarantine')
    disposition = models.CharField(
        max_length=100, blank=True)  # Rework, Scrap, Use As Is
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ncr_number} - {self.product.name}"


class SPCData(models.Model):
    parameter_name = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=10, decimal_places=4)
    timestamp = models.DateTimeField(auto_now_add=True)
    machine_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.parameter_name}: {self.value}"
