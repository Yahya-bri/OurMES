from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orders', '0001_initial'),
        ('basic', '0001_initial'),
        ('technologies', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductionCounting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('done_quantity', models.DecimalField(decimal_places=5, default=Decimal('0'), max_digits=12)),
                ('rejected_quantity', models.DecimalField(decimal_places=5, default=Decimal('0'), max_digits=12)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('component', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='production_counts', to='technologies.technologyoperationcomponent')),
                ('operation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='production_counts', to='technologies.operation')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='production_counts', to='orders.order')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='production_counts', to='basic.product')),
                ('workstation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='production_counts', to='basic.workstation')),
            ],
            options={
                'verbose_name': 'Production Counting',
                'verbose_name_plural': 'Production Countings',
                'ordering': ['-timestamp'],
            },
        ),
    ]
