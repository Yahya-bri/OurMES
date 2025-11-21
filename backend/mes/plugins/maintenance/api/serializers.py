from rest_framework import serializers
from ..domain.models import MaintenanceLog


class MaintenanceLogSerializer(serializers.ModelSerializer):
    workstation_name = serializers.CharField(
        source='workstation.name', read_only=True)
    duration_hours = serializers.ReadOnlyField()

    class Meta:
        model = MaintenanceLog
        fields = '__all__'
