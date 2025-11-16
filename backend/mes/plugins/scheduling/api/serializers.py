from rest_framework import serializers
from ..domain.models import Scheduling


class SchedulingSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.number', read_only=True)
    order_name = serializers.CharField(source='order.name', read_only=True)
    order_state = serializers.CharField(source='order.state', read_only=True)
    production_line = serializers.IntegerField(source='order.production_line_id', read_only=True)
    production_line_name = serializers.CharField(source='order.production_line.name', read_only=True)
    component_node = serializers.CharField(source='component.node_number', read_only=True)
    component_name = serializers.CharField(source='component.operation.name', read_only=True)
    operation_id = serializers.IntegerField(source='component.operation_id', read_only=True)
    operation_number = serializers.CharField(source='component.operation.number', read_only=True)
    product_number = serializers.CharField(source='order.product.number', read_only=True)
    product_name = serializers.CharField(source='order.product.name', read_only=True)
    operation_workstation_ids = serializers.SerializerMethodField()

    class Meta:
        model = Scheduling
        fields = '__all__'

    def get_operation_workstation_ids(self, obj):
        return list(obj.component.operation.workstations.values_list('id', flat=True))


class BulkSchedulingUpdateSerializer(serializers.Serializer):
    """Serializer for bulk updating multiple schedule items"""
    updates = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False
    )

    def validate_updates(self, value):
        """Validate that each update has required fields"""
        for update in value:
            if 'id' not in update:
                raise serializers.ValidationError("Each update must have an 'id' field")
            non_id_fields = [k for k in update.keys() if k != 'id']
            if not non_id_fields:
                raise serializers.ValidationError("Each update must include at least one field to modify")
        return value


class ScheduleConflictCheckSerializer(serializers.Serializer):
    """Serializer for checking schedule conflicts"""
    items = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False
    )
