from rest_framework import serializers
from ..domain.models import (
    Technology, Operation, TechnologyOperationComponent,
    OperationProductInComponent, OperationProductOutComponent
)
from mes.plugins.basic.api.serializers import ProductSerializer, WorkstationSerializer


class OperationSerializer(serializers.ModelSerializer):
    workstation_names = serializers.SerializerMethodField()
    
    def get_workstation_names(self, obj):
        return [ws.name for ws in obj.workstations.all()]
    
    class Meta:
        model = Operation
        fields = '__all__'


class OperationProductInComponentSerializer(serializers.ModelSerializer):
    product_number = serializers.CharField(source='product.number', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OperationProductInComponent
        fields = '__all__'


class OperationProductOutComponentSerializer(serializers.ModelSerializer):
    product_number = serializers.CharField(source='product.number', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OperationProductOutComponent
        fields = '__all__'


class TechnologyOperationComponentSerializer(serializers.ModelSerializer):
    operation_number = serializers.CharField(source='operation.number', read_only=True)
    operation_name = serializers.CharField(source='operation.name', read_only=True)
    input_products = OperationProductInComponentSerializer(many=True, read_only=True)
    output_products = OperationProductOutComponentSerializer(many=True, read_only=True)
    
    class Meta:
        model = TechnologyOperationComponent
        fields = '__all__'


class TechnologySerializer(serializers.ModelSerializer):
    product_number = serializers.CharField(source='product.number', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    operation_components = TechnologyOperationComponentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Technology
        fields = '__all__'


class TechnologyDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    operation_components = TechnologyOperationComponentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Technology
        fields = '__all__'
