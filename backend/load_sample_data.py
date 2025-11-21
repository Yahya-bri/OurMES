#!/usr/bin/env python
"""
Sample data loader for OurMES
Creates companies, products, technologies, and orders for testing
"""
from mes.plugins.quality.domain.models import InspectionConfig, QualityCheck, NCR, SPCData
from mes.plugins.maintenance.domain.models import MaintenanceLog
from mes.plugins.inventory.domain.models import MaterialStock, Container, TraceabilityRecord, KanbanCard
from mes.plugins.production_counting.domain.models import ProductionCounting
from mes.plugins.orders.domain.models import Order
from mes.plugins.routing.domain.models import Technology, Operation, TechnologyOperationComponent, OperationProductInComponent, OperationProductOutComponent
from django.contrib.auth.models import User, Group
from mes.plugins.basic.domain.models import Company, Product, Workstation, ProductionLine, Staff
from django.utils import timezone
import os
import sys
import django
from datetime import timedelta
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ourmes_backend.settings.dev')
django.setup()

# Now import Django models after setup


def create_companies():
    """Create sample companies"""
    print("Creating companies...")
    companies = [
        {
            'number': 'COMP001',
            'name': 'Acme Manufacturing',
            'email': 'contact@acme-mfg.com',
            'phone': '+1-555-0100',
            'city': 'New York',
            'country': 'USA'
        },
        {
            'number': 'COMP002',
            'name': 'Global Supplies Inc',
            'email': 'info@globalsupplies.com',
            'phone': '+1-555-0200',
            'city': 'Chicago',
            'country': 'USA'
        },
        {
            'number': 'COMP003',
            'name': 'TechParts Ltd',
            'email': 'sales@techparts.com',
            'phone': '+44-20-5500',
            'city': 'London',
            'country': 'UK'
        },
    ]

    created = []
    for comp_data in companies:
        comp, _ = Company.objects.get_or_create(
            number=comp_data['number'],
            defaults=comp_data
        )
        created.append(comp)
        print(f"  ✓ {comp.number} - {comp.name}")

    return created


def create_workstations(production_lines):
    """Create sample workstations mapped to production lines"""
    print("\nCreating workstations...")
    line_lookup = {line.number: line for line in production_lines}
    fallback_line = production_lines[0] if production_lines else None
    workstations_data = [
        {'number': 'WS001', 'name': 'CNC Machine 1',
            'description': 'High-precision CNC milling machine', 'line': 'LINE001'},
        {'number': 'WS002', 'name': 'CNC Machine 2',
            'description': 'Secondary CNC machine', 'line': 'LINE001'},
        {'number': 'WS003', 'name': 'Assembly Line A',
            'description': 'Primary assembly line', 'line': 'LINE001'},
        {'number': 'WS004', 'name': 'Assembly Line B',
            'description': 'Secondary assembly line', 'line': 'LINE002'},
        {'number': 'WS005', 'name': 'Quality Control Station',
            'description': 'Final quality inspection', 'line': 'LINE001'},
        {'number': 'WS006', 'name': 'Packaging Unit',
            'description': 'Product packaging station', 'line': 'LINE002'},
    ]

    created = []
    for ws_data in workstations_data:
        target_line = line_lookup.get(ws_data.get('line')) or fallback_line
        defaults = {
            'name': ws_data['name'],
            'description': ws_data['description'],
            'production_line': target_line
        }
        ws, _ = Workstation.objects.get_or_create(
            number=ws_data['number'],
            defaults=defaults
        )
        if ws.production_line_id is None and target_line:
            ws.production_line = target_line
            ws.save(update_fields=['production_line'])
        created.append(ws)
        line_label = ws.production_line.number if ws.production_line else 'UNASSIGNED'
        print(f"  ✓ {ws.number} - {ws.name} (Line {line_label})")

    return created


def create_production_lines():
    """Create sample production lines"""
    print("\nCreating production lines...")
    lines_data = [
        {'number': 'LINE001', 'name': 'Main Production Line',
            'description': 'Primary manufacturing line'},
        {'number': 'LINE002', 'name': 'Secondary Line',
            'description': 'Backup production capacity'},
    ]

    created = []
    for line_data in lines_data:
        line, _ = ProductionLine.objects.get_or_create(
            number=line_data['number'],
            defaults=line_data
        )
        created.append(line)
        print(f"  ✓ {line.number} - {line.name}")

    return created


def create_products(companies):
    """Create sample products"""
    print("\nCreating products...")
    products_data = [
        {
            'number': 'PROD001',
            'name': 'Widget Alpha',
            'global_type_of_material': 'component',
            'unit': 'pcs',
            'description': 'Basic widget component',
            'supplier': companies[0] if companies else None
        },
        {
            'number': 'PROD002',
            'name': 'Widget Beta',
            'global_type_of_material': 'component',
            'unit': 'pcs',
            'description': 'Advanced widget component',
            'supplier': companies[1] if len(companies) > 1 else None
        },
        {
            'number': 'PROD003',
            'name': 'Assembly Kit Standard',
            'global_type_of_material': 'intermediate',
            'unit': 'pcs',
            'description': 'Standard assembly kit'
        },
        {
            'number': 'PROD004',
            'name': 'Final Product X100',
            'global_type_of_material': 'final_product',
            'unit': 'pcs',
            'description': 'Complete product ready for sale',
            'producer': companies[0] if companies else None
        },
        {
            'number': 'PROD005',
            'name': 'Final Product X200',
            'global_type_of_material': 'final_product',
            'unit': 'pcs',
            'description': 'Premium product variant',
            'producer': companies[0] if companies else None
        },
    ]

    created = []
    for prod_data in products_data:
        prod, _ = Product.objects.get_or_create(
            number=prod_data['number'],
            defaults=prod_data
        )
        created.append(prod)
        print(f"  ✓ {prod.number} - {prod.name}")

    return created


def create_operations(workstations):
    """Create sample operations"""
    print("\nCreating operations...")
    ws_cycle = workstations or []
    operations_data = [
        {
            'number': 'OP001',
            'name': 'CNC Milling',
            'description': 'Precision milling operation',
            'tj': 600,  # 10 minutes per batch
            'tpz': 300,  # 5 minutes preparation
            'time_next_operation': 60,  # 1 minute to next operation
            'workstation': 'WS001'
        },
        {
            'number': 'OP002',
            'name': 'Assembly',
            'description': 'Component assembly',
            'tj': 900,  # 15 minutes per batch
            'tpz': 600,  # 10 minutes preparation
            'time_next_operation': 120,  # 2 minutes to next operation
            'workstation': 'WS003'
        },
        {
            'number': 'OP003',
            'name': 'Quality Check',
            'description': 'Final quality inspection',
            'tj': 300,  # 5 minutes per batch
            'tpz': 0,  # No preparation needed
            'time_next_operation': 60,  # 1 minute to next operation
            'workstation': 'WS005'
        },
        {
            'number': 'OP004',
            'name': 'Packaging',
            'description': 'Product packaging',
            'tj': 480,  # 8 minutes per batch
            'tpz': 180,  # 3 minutes preparation
            'time_next_operation': 0,  # Last operation
            'workstation': 'WS006'
        },
        {
            'number': 'OP005',
            'name': 'Polishing',
            'description': 'Surface finishing polish',
            'tj': 420,
            'tpz': 120,
            'time_next_operation': 60,
            'workstation': 'WS002'
        },
    ]

    created = []
    op_workstation_map = {}
    ws_lookup = {ws.number: ws for ws in workstations}
    for idx, op_data in enumerate(operations_data):
        op_defaults = op_data.copy()
        op_defaults.pop('workstation', None)
        op, _ = Operation.objects.get_or_create(
            number=op_data['number'],
            defaults=op_defaults
        )
        # Ensure timing fields updated on existing objects as well
        for attr in ('name', 'description', 'tj', 'tpz', 'time_next_operation'):
            setattr(op, attr, op_data[attr])
        op.save()
        # Add workstation relationship
        ws_number = op_data.get('workstation')
        assigned_ws = ws_lookup.get(ws_number) if ws_number else (
            ws_cycle[idx % len(ws_cycle)] if ws_cycle else None)
        if assigned_ws:
            op.workstations.set([assigned_ws])
            op_workstation_map[op.number] = assigned_ws
        created.append(op)
        print(f"  ✓ {op.number} - {op.name}")

    return created, op_workstation_map


def create_technologies(products, operations):
    """Create sample technologies"""
    print("\nCreating technologies...")
    ops_map = {op.number: op for op in operations}

    # Technology for Final Product X100
    if len(products) >= 4 and {'OP001', 'OP002', 'OP003', 'OP004'}.issubset(ops_map.keys()):
        tech1, _ = Technology.objects.get_or_create(
            number='ROUTE001',
            defaults={
                'name': 'Standard Production Process',
                'description': 'Standard manufacturing process for X100',
                'product': products[3],  # Final Product X100
                'state': 'accepted',
                'active': True
            }
        )
        print(f"  ✓ {tech1.number} - {tech1.name}")

        # Add operations to technology
        toc1, _ = TechnologyOperationComponent.objects.get_or_create(
            technology=tech1,
            operation=ops_map['OP001'],  # CNC Milling
            defaults={'node_number': '1', 'priority': 10}
        )

        toc2, _ = TechnologyOperationComponent.objects.get_or_create(
            technology=tech1,
            operation=ops_map['OP002'],  # Assembly
            defaults={'node_number': '1.1', 'priority': 20, 'parent': toc1}
        )

        toc3, _ = TechnologyOperationComponent.objects.get_or_create(
            technology=tech1,
            operation=ops_map['OP003'],  # Quality Check
            defaults={'node_number': '1.1.1', 'priority': 30, 'parent': toc2}
        )

        toc4, _ = TechnologyOperationComponent.objects.get_or_create(
            technology=tech1,
            operation=ops_map['OP004'],  # Packaging
            defaults={'node_number': '1.1.1.1', 'priority': 40, 'parent': toc3}
        )

        # Add input components (materials)
        OperationProductInComponent.objects.get_or_create(
            operation_component=toc1,
            product=products[0],  # Widget Alpha
            defaults={'quantity': Decimal('2.00')}
        )

        OperationProductInComponent.objects.get_or_create(
            operation_component=toc2,
            product=products[1],  # Widget Beta
            defaults={'quantity': Decimal('3.00')}
        )

        # Add output product
        OperationProductOutComponent.objects.get_or_create(
            operation_component=toc4,
            product=products[3],  # Final Product X100
            defaults={'quantity': Decimal('1.00')}
        )

        print(f"    ✓ Added 4 operations with components")

        # Technology for Final Product X200
        tech2, _ = Technology.objects.get_or_create(
            number='ROUTE002',
            defaults={
                'name': 'Premium Production Process',
                'description': 'Premium manufacturing process for X200',
                'product': products[4],  # Final Product X200
                'state': 'accepted',
                'active': True
            }
        )
        print(f"  ✓ {tech2.number} - {tech2.name}")

        if 'OP005' in ops_map:
            premium_root, _ = TechnologyOperationComponent.objects.get_or_create(
                technology=tech2,
                operation=ops_map['OP001'],
                defaults={'node_number': '1', 'priority': 5}
            )
            premium_polish, _ = TechnologyOperationComponent.objects.get_or_create(
                technology=tech2,
                operation=ops_map['OP005'],
                defaults={'node_number': '1.2',
                          'priority': 25, 'parent': premium_root}
            )
            OperationProductOutComponent.objects.get_or_create(
                operation_component=premium_polish,
                product=products[4],
                defaults={'quantity': Decimal('1.00')}
            )
        return [tech1, tech2]

    return []


def create_orders(products, technologies, companies, production_lines):
    """Create sample orders with timezone-aware datetimes for consistency"""
    print("\nCreating orders...")

    if not products or not technologies:
        print("  ⚠ Skipping orders - no products or technologies available")
        return []

    now = timezone.now()
    orders_data = [
        {
            'number': 'ORD001',
            'name': 'Customer Order #1001',
            'product': products[3],  # Final Product X100
            'technology': technologies[0],
            'planned_quantity': Decimal('100.00'),
            'state': 'pending',
            'date_from': now,
            'date_to': now + timedelta(days=7),
            'deadline': now + timedelta(days=7),
            'company': companies[0] if companies else None,
            'production_line': production_lines[0] if production_lines else None
        },
        {
            'number': 'ORD002',
            'name': 'Customer Order #1002',
            'product': products[3],  # Final Product X100
            'technology': technologies[0],
            'planned_quantity': Decimal('50.00'),
            'state': 'in_progress',
            'date_from': now - timedelta(days=2),
            'date_to': now + timedelta(days=5),
            'deadline': now + timedelta(days=5),
            'company': companies[1] if len(companies) > 1 else None,
            'production_line': production_lines[0] if production_lines else None
        },
        {
            'number': 'ORD003',
            'name': 'Customer Order #1003',
            'product': products[4],  # Final Product X200
            'technology': technologies[1] if len(technologies) > 1 else None,
            'planned_quantity': Decimal('75.00'),
            'state': 'pending',
            'date_from': now + timedelta(days=3),
            'date_to': now + timedelta(days=10),
            'deadline': now + timedelta(days=10),
            'company': companies[2] if len(companies) > 2 else None,
            'production_line': production_lines[1] if len(production_lines) > 1 else None
        },
        {
            'number': 'ORD004',
            'name': 'Customer Order #1004',
            'product': products[3],  # Final Product X100
            'technology': technologies[0],
            'planned_quantity': Decimal('200.00'),
            'state': 'completed',
            'date_from': now - timedelta(days=10),
            'date_to': now - timedelta(days=1),
            'deadline': now - timedelta(days=1),
            'done_quantity': Decimal('200.00'),
            'company': companies[0] if companies else None,
            'production_line': production_lines[0] if production_lines else None
        },
    ]

    created = []
    for order_data in orders_data:
        order, _ = Order.objects.get_or_create(
            number=order_data['number'],
            defaults=order_data
        )
        created.append(order)
        print(f"  ✓ {order.number} - {order.name} [{order.state}]")

    return created


def create_staff():
    """Create sample staff/operators for production counting"""
    print("\nCreating staff...")
    staff_data = [
        {'number': 'EMP001', 'name': 'Alice', 'surname': 'Smith',
            'email': 'alice@example.com', 'phone': '+1-555-1111'},
        {'number': 'EMP002', 'name': 'Bob', 'surname': 'Johnson',
            'email': 'bob@example.com', 'phone': '+1-555-2222'},
        {'number': 'EMP003', 'name': 'Carol', 'surname': 'Davis',
            'email': 'carol@example.com', 'phone': '+1-555-3333'},
    ]
    created = []
    for s in staff_data:
        staff, _ = Staff.objects.get_or_create(number=s['number'], defaults=s)
        created.append(staff)
        print(f"  ✓ {staff.number} - {staff.name} {staff.surname}")
    return created


def create_users_and_roles():
    """Create default users and assign RBAC groups for demo/testing."""
    print("\nCreating users and roles...")
    # Ensure groups exist
    for role in ['Operator', 'Planner', 'Supervisor', 'Admin']:
        Group.objects.get_or_create(name=role)

    users_data = [
        ("operator", "operator", ["Operator"]),
        ("planner", "planner", ["Planner"]),
        ("supervisor", "supervisor", ["Supervisor"]),
        ("admin", "admin", ["Admin"]),
    ]

    created_users = []
    for username, password, roles in users_data:
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password(password)
            # Make admin staff for admin UI access
            if 'Admin' in roles:
                user.is_staff = True
                user.is_superuser = True
            user.save()
        # Assign groups
        for role in roles:
            grp = Group.objects.get(name=role)
            user.groups.add(grp)
        created_users.append(user)
        print(f"  ✓ user '{username}' (roles: {', '.join(roles)})")
    return created_users


def create_production_counts(orders, operations, staff, op_workstation_map):
    """Seed production-counting records to reflect progress."""
    print("\nCreating production counting records...")
    if not orders:
        print("  ⚠ Skipping production counts - no orders")
        return []
    records = []
    ops_map = {op.number: op for op in operations}
    staff_cycle = staff or [None]
    now = timezone.now()
    order_lookup = {order.number: order for order in orders}
    sample_records = [
        {
            'order': 'ORD002',
            'operation': 'OP002',
            'produced': Decimal('20.00'),
            'scrap': Decimal('1.00'),
            'status': 'in_progress',
            'start_offset': timedelta(hours=-2),
            'staff_idx': 0
        },
        {
            'order': 'ORD004',
            'operation': 'OP004',
            'produced': Decimal('200.00'),
            'scrap': Decimal('2.00'),
            'status': 'completed',
            'start_offset': timedelta(days=-1, hours=-3),
            'end_offset': timedelta(days=-1, hours=-1),
            'staff_idx': 1
        },
    ]
    for payload in sample_records:
        order = order_lookup.get(payload['order'])
        operation = ops_map.get(payload['operation'])
        if not order or not operation:
            continue
        start_time = now + payload.get('start_offset', timedelta())
        end_time = None
        if payload['status'] == 'completed':
            end_time = now + payload.get('end_offset', timedelta())
        record, _ = ProductionCounting.objects.get_or_create(
            order=order,
            operation=operation,
            defaults={
                'product': order.product,
                'workstation': op_workstation_map.get(operation.number),
                'done_quantity': payload['produced'],
                'rejected_quantity': payload['scrap'],
                'status': payload['status'],
                'start_time': start_time,
                'end_time': end_time,
                'operator': staff_cycle[payload.get('staff_idx', 0)]
            }
        )
        records.append(record)
        print(
            f"  ✓ Production record for {record.order.number} - {operation.number} ({record.status})")
    return records


def create_inventory_data(products):
    """Create sample inventory data"""
    print("\nCreating inventory data...")
    if not products:
        print("  ⚠ Skipping inventory - no products")
        return []

    # Material Stock
    stocks = [
        MaterialStock.objects.get_or_create(
            material=products[0],
            location_name='Warehouse A1',
            defaults={'location_type': 'warehouse', 'quantity': Decimal(
                '500'), 'batch_number': 'B-2023-001'}
        )[0],
        MaterialStock.objects.get_or_create(
            material=products[1],
            location_name='Shop Floor - CNC',
            defaults={'location_type': 'shop_floor', 'quantity': Decimal('50')}
        )[0],
    ]
    print(f"  ✓ Created {len(stocks)} stock records")

    # Containers
    containers = [
        Container.objects.get_or_create(
            container_id='BIN-101',
            defaults={'type': 'bin', 'content_material': products[0], 'content_quantity': Decimal(
                '100'), 'location': 'Warehouse A1'}
        )[0],
        Container.objects.get_or_create(
            container_id='PAL-205',
            defaults={'type': 'pallet', 'content_material': products[3], 'content_quantity': Decimal(
                '20'), 'location': 'Shipping Dock'}
        )[0],
    ]
    print(f"  ✓ Created {len(containers)} containers")

    # Traceability
    traces = [
        TraceabilityRecord.objects.get_or_create(
            finished_good_batch='FG-2023-100',
            raw_material_batch='RM-2023-050',
            defaults={
                'finished_good': products[3], 'raw_material': products[0], 'quantity_used': Decimal('200')}
        )[0],
    ]
    print(f"  ✓ Created {len(traces)} traceability records")

    # Kanban Cards
    kanbans = [
        KanbanCard.objects.get_or_create(
            material=products[0],
            location='Assembly Line 1',
            defaults={'capacity': Decimal('500'), 'status': 'full'}
        )[0],
        KanbanCard.objects.get_or_create(
            material=products[1],
            location='CNC Center',
            defaults={'capacity': Decimal('200'), 'status': 'replenishing'}
        )[0],
    ]
    print(f"  ✓ Created {len(kanbans)} kanban cards")

    return stocks + containers + traces + kanbans


def create_maintenance_data(workstations):
    """Create sample maintenance logs"""
    print("\nCreating maintenance data...")
    if not workstations:
        print("  ⚠ Skipping maintenance - no workstations")
        return []

    now = timezone.now()
    logs = [
        MaintenanceLog.objects.get_or_create(
            workstation=workstations[0],
            start_time=now - timedelta(days=5),
            defaults={
                'type': 'preventive',
                'description': 'Routine maintenance check',
                'end_time': now - timedelta(days=5, hours=-2),
                'technician_name': 'John Doe'
            }
        )[0],
        MaintenanceLog.objects.get_or_create(
            workstation=workstations[0],
            start_time=now - timedelta(days=15),
            defaults={
                'type': 'corrective',
                'description': 'Bearing replacement',
                'end_time': now - timedelta(days=15, hours=-4),
                'technician_name': 'Jane Smith'
            }
        )[0],
    ]
    print(f"  ✓ Created {len(logs)} maintenance logs")
    return logs


def create_quality_data(operations, products):
    """Create sample quality data"""
    print("\nCreating quality data...")
    if not operations or not products:
        print("  ⚠ Skipping quality - no operations or products")
        return []

    # Inspection Configs
    configs = [
        InspectionConfig.objects.get_or_create(
            operation=operations[0],
            defaults={
                'check_type': 'variable',
                'description': 'Diameter measurement',
                'parameters': '10.0 +/- 0.05mm',
                'mandatory': True
            }
        )[0],
        InspectionConfig.objects.get_or_create(
            operation=operations[1],
            defaults={
                'check_type': 'pass_fail',
                'description': 'Visual inspection',
                'parameters': '',
                'mandatory': True
            }
        )[0],
    ]
    print(f"  ✓ Created {len(configs)} inspection configs")

    # NCRs
    ncrs = [
        NCR.objects.get_or_create(
            ncr_number='NCR-2023-055',
            defaults={
                'product': products[3],
                'issue_description': 'Surface scratch > 2mm',
                'status': 'quarantine',
                'disposition': ''
            }
        )[0],
    ]
    print(f"  ✓ Created {len(ncrs)} NCRs")

    # SPC Data
    spc_data = []
    for i in range(10):
        spc = SPCData.objects.create(
            parameter_name='Diameter',
            value=Decimal('10.0') + Decimal(str((i - 5) * 0.01)),
            machine_id='CNC-A'
        )
        spc_data.append(spc)
    print(f"  ✓ Created {len(spc_data)} SPC data points")

    return configs + ncrs + spc_data


def main():
    """Main entry point"""
    print("=" * 60)
    print("OurMES Sample Data Loader")
    print("=" * 60)

    # Create data in order of dependencies
    companies = create_companies()
    production_lines = create_production_lines()
    workstations = create_workstations(production_lines)
    products = create_products(companies)
    staff = create_staff()
    operations, op_workstation_map = create_operations(workstations)
    technologies = create_technologies(products, operations)
    orders = create_orders(products, technologies, companies, production_lines)
    create_users_and_roles()
    production_counts = create_production_counts(
        orders, operations, staff, op_workstation_map)

    # Create new feature data
    inventory_items = create_inventory_data(products)
    maintenance_logs = create_maintenance_data(workstations)
    quality_items = create_quality_data(operations, products)

    print("\n" + "=" * 60)
    print("✓ Sample data loaded successfully!")
    print("=" * 60)
    print(f"Companies: {len(companies)}")
    print(f"Workstations: {len(workstations)}")
    print(f"Production Lines: {len(production_lines)}")
    print(f"Products: {len(products)}")
    print(f"Operations: {len(operations)}")
    print(f"Technologies: {len(technologies)}")
    print(f"Staff: {len(staff)}")
    print(f"Orders: {len(orders)}")
    print(f"Production Counts: {len(production_counts)}")
    print(f"Inventory Items: {len(inventory_items)}")
    print(f"Maintenance Logs: {len(maintenance_logs)}")
    print(f"Quality Items: {len(quality_items)}")
    print("Users: operator/planner/supervisor/admin (passwords same as usernames)")
    print("=" * 60)


if __name__ == '__main__':
    main()
