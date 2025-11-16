from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Company(models.Model):
    """Company model representing suppliers, customers, and producers"""
    number = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    tax = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    street = models.CharField(max_length=255, blank=True)
    house = models.CharField(max_length=30, blank=True)
    flat = models.CharField(max_length=30, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ['name']

    def __str__(self):
        return f"{self.number} - {self.name}"


class Product(models.Model):
    """Product model with support for components, intermediates, and final products"""
    TYPE_CHOICES = [
        ('component', 'Component'),
        ('intermediate', 'Intermediate'),
        ('final_product', 'Final Product'),
        ('waste', 'Waste'),
        ('package', 'Package'),
    ]
    
    ENTITY_TYPE_CHOICES = [
        ('particular_product', 'Particular Product'),
        ('products_family', 'Products Family'),
    ]

    number = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=1024)
    global_type_of_material = models.CharField(max_length=20, choices=TYPE_CHOICES, default='component')
    ean = models.CharField(max_length=50, blank=True, unique=True, null=True)
    unit = models.CharField(max_length=10, default='pcs')
    external_number = models.CharField(max_length=255, blank=True, unique=True, null=True)
    description = models.TextField(max_length=2048, blank=True)
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPE_CHOICES, default='particular_product')
    
    # Relationships
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    producer = models.ForeignKey(Company, null=True, blank=True, on_delete=models.SET_NULL, related_name='produced_products')
    supplier = models.ForeignKey(Company, null=True, blank=True, on_delete=models.SET_NULL, related_name='supplied_products')
    
    # Additional fields
    additional_unit = models.CharField(max_length=10, blank=True)
    conversion = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, validators=[MinValueValidator(Decimal('0.00001'))])
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['number']

    def __str__(self):
        return f"{self.number} - {self.name}"


class Workstation(models.Model):
    """Workstation model representing production machines and work centers"""
    number = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=1024)
    description = models.TextField(blank=True)
    production_line = models.ForeignKey(
        'ProductionLine',
        on_delete=models.CASCADE,
        related_name='workstations',
        null=True,
        blank=True
    )
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Workstation"
        verbose_name_plural = "Workstations"
        ordering = ['number']

    def __str__(self):
        return f"{self.number} - {self.name}"


class ProductionLine(models.Model):
    """Production line model"""
    number = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=1024)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Production Line"
        verbose_name_plural = "Production Lines"
        ordering = ['number']

    def __str__(self):
        return f"{self.number} - {self.name}"


class Staff(models.Model):
    """Staff/Worker model"""
    number = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Staff"
        verbose_name_plural = "Staff"
        ordering = ['surname', 'name']

    def __str__(self):
        return f"{self.number} - {self.name} {self.surname}"
