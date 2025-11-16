from rest_framework import viewsets
from .models import Modeler
from .serializers import ModelerSerializer


class ModelerViewSet(viewsets.ModelViewSet):
    queryset = Modeler.objects.all()
    serializer_class = ModelerSerializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()