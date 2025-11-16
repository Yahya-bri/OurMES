from rest_framework import viewsets
from ..application.services import DeliveryService
from ..domain.models import Delivery
from .serializers import DeliverySerializer

class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer

    def perform_create(self, serializer):
        delivery = DeliveryService.create_delivery(**serializer.validated_data)
        serializer.instance = delivery

    def perform_update(self, serializer):
        delivery = DeliveryService.update_delivery(serializer.instance, **serializer.validated_data)
        serializer.instance = delivery

    def perform_destroy(self, instance):
        DeliveryService.delete_delivery(instance)
