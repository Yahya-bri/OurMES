from django.db import migrations, models


def assign_production_lines(apps, schema_editor):
    Workstation = apps.get_model('basic', 'Workstation')
    ProductionLine = apps.get_model('basic', 'ProductionLine')
    db_alias = schema_editor.connection.alias

    # Attempt to load the historical through model for the many-to-many relation
    try:
        LineThrough = apps.get_model('basic', 'ProductionLine_workstations')
    except LookupError:
        LineThrough = None

    assignments = {}
    if LineThrough is not None:
        for rel in LineThrough.objects.using(db_alias).all():
            # Preserve the first production line seen for the workstation
            assignments.setdefault(rel.workstation_id, rel.productionline_id)

    default_line = None

    # Helper to lazily create a fallback production line if none exist
    def get_default_line():
        nonlocal default_line
        if default_line is not None:
            return default_line
        default_line = ProductionLine.objects.using(db_alias).order_by('id').first()
        if default_line is None:
            default_line = ProductionLine.objects.using(db_alias).filter(number='LINE-DEFAULT').first()
        if default_line is None:
            default_line = ProductionLine.objects.using(db_alias).create(
                number='LINE-DEFAULT',
                name='Default Line',
                description='Auto-generated line for orphaned workstations',
                active=True,
            )
        return default_line

    for workstation in Workstation.objects.using(db_alias).all():
        line_id = assignments.get(workstation.id)
        if line_id is None:
            default = get_default_line()
            line_id = default.id
        workstation.production_line_id = line_id
        workstation.save(update_fields=['production_line'])


class Migration(migrations.Migration):

    dependencies = [
        ('basic', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='workstation',
            name='production_line',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.CASCADE,
                related_name='workstations',
                to='basic.productionline',
            ),
        ),
        migrations.RunPython(assign_production_lines, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='productionline',
            name='workstations',
        ),
    ]
