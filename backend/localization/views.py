from rest_framework import viewsets
from .models import Localization
from .serializers import LocalizationSerializer

class LocalizationViewSet(viewsets.ModelViewSet):
    queryset = Localization.objects.all()
    serializer_class = LocalizationSerializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()