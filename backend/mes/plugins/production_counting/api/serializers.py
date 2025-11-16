from rest_framework import serializers
from ..domain.models import ProductionCounting
from mes.plugins.basic.domain.models import Staff


class ProductionCountingSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.number', read_only=True)
    operation_number = serializers.CharField(source='operation.number', read_only=True)
    operation_name = serializers.CharField(source='operation.name', read_only=True)
    product_number = serializers.CharField(source='product.number', read_only=True)
    workstation_number = serializers.CharField(source='workstation.number', read_only=True)
    workstation_name = serializers.CharField(source='workstation.name', read_only=True)
    operator_name = serializers.SerializerMethodField()
    net_quantity = serializers.DecimalField(max_digits=12, decimal_places=5, read_only=True)
    # frontend field aliases
    produced_quantity = serializers.DecimalField(source='done_quantity', max_digits=12, decimal_places=5, required=False)
    scrap_quantity = serializers.DecimalField(source='rejected_quantity', max_digits=12, decimal_places=5, required=False)

    class Meta:
        model = ProductionCounting
        fields = '__all__'

    def get_operator_name(self, obj):
        if obj.operator_id:
            return f"{obj.operator.name} {obj.operator.surname}"
        return None
