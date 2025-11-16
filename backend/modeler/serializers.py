from rest_framework import serializers
from .models import Modeler


class ModelerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modeler
        fields = '__all__'
