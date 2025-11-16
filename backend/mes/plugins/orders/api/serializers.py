from rest_framework import serializers
from ..domain.models import Order, OrderStateChange
from mes.plugins.basic.api.serializers import CompanySerializer, ProductSerializer, ProductionLineSerializer
from mes.plugins.routing.api.serializers import TechnologySerializer


class OrderStateChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStateChange
        fields = '__all__'
        read_only_fields = ['date_and_time']


class OrderSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_number = serializers.CharField(source='product.number', read_only=True)
    technology_name = serializers.CharField(source='technology.name', read_only=True)
    production_line_name = serializers.CharField(source='production_line.name', read_only=True)
    state_changes = OrderStateChangeSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'

    def validate_external_number(self, value):
        # Normalize blank strings to None so unique constraint is not violated by '' duplicates
        if not value:
            return None
        return value


class OrderDetailSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    technology = TechnologySerializer(read_only=True)
    production_line = ProductionLineSerializer(read_only=True)
    state_changes = OrderStateChangeSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
