"""
Master Data Services.

Business logic for managing core entities: companies, products,
workstations, production lines, and staff.
"""
from django.db import transaction
from django.db.models import Count, Q, Prefetch

from core.base.services import BaseService
from core.base.exceptions import ValidationException, BusinessRuleException
from ..domain.models import Company, Product, Workstation, ProductionLine, Staff


class CompanyService(BaseService):
    """Service for managing companies (suppliers, customers, producers)."""
    model = Company

    @classmethod
    def get_active(cls):
        """Get all active companies."""
        return cls.get_queryset().filter(active=True)

    @classmethod
    def get_suppliers(cls):
        """Get companies that are suppliers (have supplied products)."""
        return cls.get_active().filter(supplied_products__isnull=False).distinct()

    @classmethod
    def get_producers(cls):
        """Get companies that are producers."""
        return cls.get_active().filter(produced_products__isnull=False).distinct()

    @classmethod
    def search(cls, query: str):
        """Search companies by number, name, or email."""
        return cls.get_queryset().filter(
            Q(number__icontains=query) |
            Q(name__icontains=query) |
            Q(email__icontains=query)
        )

    @classmethod
    @transaction.atomic
    def deactivate(cls, company: Company) -> Company:
        """Deactivate a company."""
        company.active = False
        company.save(update_fields=['active', 'updated_at'])
        return company

    @classmethod
    @transaction.atomic
    def bulk_activate(cls, ids: list) -> int:
        """Activate multiple companies."""
        return cls.get_queryset().filter(id__in=ids).update(active=True)

    @classmethod
    @transaction.atomic
    def bulk_deactivate(cls, ids: list) -> int:
        """Deactivate multiple companies."""
        return cls.get_queryset().filter(id__in=ids).update(active=False)


class ProductService(BaseService):
    """Service for managing products and materials."""
    model = Product

    @classmethod
    def get_active(cls):
        """Get all active products."""
        return cls.get_queryset().filter(active=True)

    @classmethod
    def get_by_type(cls, product_type: str):
        """Get products by type (component, intermediate, final_product, etc.)."""
        return cls.get_active().filter(global_type_of_material=product_type)

    @classmethod
    def get_final_products(cls):
        """Get all final products."""
        return cls.get_by_type('final_product')

    @classmethod
    def get_components(cls):
        """Get all component products."""
        return cls.get_by_type('component')

    @classmethod
    def get_by_supplier(cls, supplier_id: int):
        """Get products from a specific supplier."""
        return cls.get_active().filter(supplier_id=supplier_id)

    @classmethod
    def get_by_producer(cls, producer_id: int):
        """Get products from a specific producer."""
        return cls.get_active().filter(producer_id=producer_id)

    @classmethod
    def search(cls, query: str):
        """Search products by number, name, or EAN."""
        return cls.get_queryset().filter(
            Q(number__icontains=query) |
            Q(name__icontains=query) |
            Q(ean__icontains=query)
        )

    @classmethod
    def get_with_children(cls, product_id: int):
        """Get a product with its child products (family)."""
        return cls.get_queryset().prefetch_related('children').get(id=product_id)

    @classmethod
    def get_product_tree(cls, product_id: int) -> dict:
        """Get hierarchical product structure."""
        product = cls.get_by_id(product_id)

        def build_tree(p):
            return {
                'id': p.id,
                'number': p.number,
                'name': p.name,
                'type': p.global_type_of_material,
                'children': [build_tree(child) for child in p.children.all()]
            }

        return build_tree(product)

    @classmethod
    @transaction.atomic
    def deactivate(cls, product: Product) -> Product:
        """Deactivate a product."""
        product.active = False
        product.save(update_fields=['active', 'updated_at'])
        return product

    @classmethod
    def stats(cls):
        """Get product statistics by type."""
        return cls.get_queryset().aggregate(
            total=Count('id'),
            active=Count('id', filter=Q(active=True)),
            components=Count('id', filter=Q(global_type_of_material='component')),
            intermediates=Count('id', filter=Q(global_type_of_material='intermediate')),
            final_products=Count('id', filter=Q(global_type_of_material='final_product')),
        )


class WorkstationService(BaseService):
    """Service for managing workstations."""
    model = Workstation

    @classmethod
    def get_active(cls):
        """Get all active workstations."""
        return cls.get_queryset().filter(active=True)

    @classmethod
    def get_by_production_line(cls, line_id: int):
        """Get workstations on a specific production line."""
        return cls.get_active().filter(production_line_id=line_id)

    @classmethod
    def get_unassigned(cls):
        """Get workstations not assigned to any production line."""
        return cls.get_active().filter(production_line__isnull=True)

    @classmethod
    @transaction.atomic
    def assign_to_line(cls, workstation: Workstation, line_id: int) -> Workstation:
        """Assign workstation to a production line."""
        workstation.production_line_id = line_id
        workstation.save(update_fields=['production_line_id', 'updated_at'])
        return workstation

    @classmethod
    @transaction.atomic
    def unassign_from_line(cls, workstation: Workstation) -> Workstation:
        """Remove workstation from its production line."""
        workstation.production_line_id = None
        workstation.save(update_fields=['production_line_id', 'updated_at'])
        return workstation

    @classmethod
    def search(cls, query: str):
        """Search workstations by number or name."""
        return cls.get_queryset().filter(
            Q(number__icontains=query) |
            Q(name__icontains=query)
        )

    @classmethod
    @transaction.atomic
    def bulk_activate(cls, ids: list) -> int:
        """Activate multiple workstations."""
        return cls.get_queryset().filter(id__in=ids).update(active=True)

    @classmethod
    @transaction.atomic
    def bulk_deactivate(cls, ids: list) -> int:
        """Deactivate multiple workstations."""
        return cls.get_queryset().filter(id__in=ids).update(active=False)


class ProductionLineService(BaseService):
    """Service for managing production lines."""
    model = ProductionLine

    @classmethod
    def get_active(cls):
        """Get all active production lines."""
        return cls.get_queryset().filter(active=True)

    @classmethod
    def get_with_workstations(cls, line_id: int = None):
        """Get production line(s) with their workstations."""
        queryset = cls.get_queryset().prefetch_related(
            Prefetch('workstations', queryset=Workstation.objects.filter(active=True))
        )
        if line_id:
            return queryset.get(id=line_id)
        return queryset

    @classmethod
    def get_line_capacity(cls, line_id: int) -> dict:
        """Get capacity info for a production line."""
        line = cls.get_with_workstations(line_id)
        return {
            'line_id': line.id,
            'line_name': line.name,
            'workstation_count': line.workstations.count(),
            'workstations': [
                {'id': ws.id, 'number': ws.number, 'name': ws.name}
                for ws in line.workstations.all()
            ]
        }

    @classmethod
    def search(cls, query: str):
        """Search production lines by number or name."""
        return cls.get_queryset().filter(
            Q(number__icontains=query) |
            Q(name__icontains=query)
        )

    @classmethod
    def stats(cls):
        """Get production line statistics."""
        return cls.get_queryset().aggregate(
            total=Count('id'),
            active=Count('id', filter=Q(active=True)),
            with_workstations=Count('id', filter=Q(workstations__isnull=False), distinct=True),
        )


class StaffService(BaseService):
    """Service for managing staff/workers."""
    model = Staff

    @classmethod
    def get_active(cls):
        """Get all active staff members."""
        return cls.get_queryset().filter(active=True)

    @classmethod
    def search(cls, query: str):
        """Search staff by number, name, surname, or email."""
        return cls.get_queryset().filter(
            Q(number__icontains=query) |
            Q(name__icontains=query) |
            Q(surname__icontains=query) |
            Q(email__icontains=query)
        )

    @classmethod
    def get_by_full_name(cls, name: str, surname: str):
        """Get staff member by full name."""
        return cls.get_queryset().filter(
            name__iexact=name,
            surname__iexact=surname
        ).first()

    @classmethod
    @transaction.atomic
    def deactivate(cls, staff: Staff) -> Staff:
        """Deactivate a staff member."""
        staff.active = False
        staff.save(update_fields=['active', 'updated_at'])
        return staff

    @classmethod
    @transaction.atomic
    def bulk_activate(cls, ids: list) -> int:
        """Activate multiple staff members."""
        return cls.get_queryset().filter(id__in=ids).update(active=True)

    @classmethod
    @transaction.atomic
    def bulk_deactivate(cls, ids: list) -> int:
        """Deactivate multiple staff members."""
        return cls.get_queryset().filter(id__in=ids).update(active=False)

    @classmethod
    def stats(cls):
        """Get staff statistics."""
        return cls.get_queryset().aggregate(
            total=Count('id'),
            active=Count('id', filter=Q(active=True)),
        )
