from rest_framework import serializers
from ..domain.models import MaterialStock, Container, TraceabilityRecord, KanbanCard


class MaterialStockSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(
        source='material.name', read_only=True)
    material_unit = serializers.CharField(
        source='material.unit', read_only=True)

    class Meta:
        model = MaterialStock
        fields = '__all__'


class ContainerSerializer(serializers.ModelSerializer):
    content_material_name = serializers.CharField(
        source='content_material.name', read_only=True)

    class Meta:
        model = Container
        fields = '__all__'


class TraceabilityRecordSerializer(serializers.ModelSerializer):
    finished_good_name = serializers.CharField(
        source='finished_good.name', read_only=True)
    raw_material_name = serializers.CharField(
        source='raw_material.name', read_only=True)

    class Meta:
        model = TraceabilityRecord
        fields = '__all__'


class KanbanCardSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(
        source='material.name', read_only=True)

    class Meta:
        model = KanbanCard
        fields = '__all__'
