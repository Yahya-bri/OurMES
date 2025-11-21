from rest_framework import viewsets
from ..domain.models import MaintenanceLog
from .serializers import MaintenanceLogSerializer


class MaintenanceLogViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceLog.objects.all()
    serializer_class = MaintenanceLogSerializer
    filterset_fields = ['workstation', 'type']
