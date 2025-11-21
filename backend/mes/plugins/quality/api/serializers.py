from rest_framework import serializers
from ..domain.models import InspectionConfig, QualityCheck, NCR, SPCData


class InspectionConfigSerializer(serializers.ModelSerializer):
    operation_name = serializers.CharField(
        source='operation.name', read_only=True)

    class Meta:
        model = InspectionConfig
        fields = '__all__'


class QualityCheckSerializer(serializers.ModelSerializer):
    config_description = serializers.CharField(
        source='config.description', read_only=True)

    class Meta:
        model = QualityCheck
        fields = '__all__'


class NCRSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = NCR
        fields = '__all__'


class SPCDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SPCData
        fields = '__all__'
