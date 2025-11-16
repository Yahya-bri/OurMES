from rest_framework import serializers
from ..domain.models import Company, Product, Workstation, ProductionLine, Staff


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    producer_name = serializers.CharField(source='producer.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'


class WorkstationSerializer(serializers.ModelSerializer):
    production_line_name = serializers.CharField(source='production_line.name', read_only=True)

    class Meta:
        model = Workstation
        fields = '__all__'
        extra_kwargs = {
            'production_line': {'required': True, 'allow_null': False}
        }


class ProductionLineSerializer(serializers.ModelSerializer):
    workstations = WorkstationSerializer(many=True, read_only=True)
    workstation_ids = serializers.PrimaryKeyRelatedField(
        source='workstations',
        many=True,
        read_only=True
    )
    
    class Meta:
        model = ProductionLine
        fields = '__all__'


class StaffSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    def get_full_name(self, obj):
        return f"{obj.name} {obj.surname}"
    
    class Meta:
        model = Staff
        fields = '__all__'
