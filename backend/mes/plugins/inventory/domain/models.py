from django.db import models
from mes.plugins.basic.domain.models import Product


class MaterialStock(models.Model):
    LOCATION_CHOICES = [
        ('warehouse', 'Warehouse'),
        ('shop_floor', 'Shop Floor'),
        ('buffer', 'Buffer Zone'),
    ]

    material = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='stocks')
    location_type = models.CharField(max_length=20, choices=LOCATION_CHOICES)
    # e.g., "Warehouse A1", "Assembly Line 1"
    location_name = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    batch_number = models.CharField(max_length=100, blank=True, null=True)
    expiry_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('material', 'location_name', 'batch_number')

    def __str__(self):
        return f"{self.material.name} - {self.location_name} ({self.quantity})"


class Container(models.Model):
    CONTAINER_TYPES = [
        ('bin', 'Bin'),
        ('tote', 'Tote'),
        ('pallet', 'Pallet'),
    ]

    container_id = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=20, choices=CONTAINER_TYPES)
    content_material = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True)
    content_quantity = models.DecimalField(
        max_digits=15, decimal_places=4, default=0)
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.container_id} ({self.type})"


class TraceabilityRecord(models.Model):
    finished_good_batch = models.CharField(max_length=100)
    finished_good = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='traceability_outputs')
    raw_material_batch = models.CharField(max_length=100)
    raw_material = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='traceability_inputs')
    quantity_used = models.DecimalField(max_digits=15, decimal_places=4)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.finished_good_batch} <- {self.raw_material_batch}"


class KanbanCard(models.Model):
    STATUS_CHOICES = [
        ('full', 'Full'),
        ('replenishing', 'Replenishing'),
        ('empty', 'Empty'),
    ]

    material = models.ForeignKey(Product, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    capacity = models.DecimalField(max_digits=15, decimal_places=4)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='full')
    last_replenished = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Kanban: {self.material.name} @ {self.location}"
