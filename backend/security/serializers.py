from rest_framework import serializers
from .models import SecurityItem


class SecurityItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityItem
        fields = '__all__'
