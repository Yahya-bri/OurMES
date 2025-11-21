from rest_framework import viewsets
from ..domain.models import InspectionConfig, QualityCheck, NCR, SPCData
from .serializers import InspectionConfigSerializer, QualityCheckSerializer, NCRSerializer, SPCDataSerializer


class InspectionConfigViewSet(viewsets.ModelViewSet):
    queryset = InspectionConfig.objects.all()
    serializer_class = InspectionConfigSerializer
    filterset_fields = ['operation']


class QualityCheckViewSet(viewsets.ModelViewSet):
    queryset = QualityCheck.objects.all()
    serializer_class = QualityCheckSerializer
    filterset_fields = ['order_number', 'config']


class NCRViewSet(viewsets.ModelViewSet):
    queryset = NCR.objects.all()
    serializer_class = NCRSerializer
    filterset_fields = ['status', 'product']


class SPCDataViewSet(viewsets.ModelViewSet):
    queryset = SPCData.objects.all()
    serializer_class = SPCDataSerializer
    filterset_fields = ['parameter_name', 'machine_id']
