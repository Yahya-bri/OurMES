from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from ..domain.models import Company, Product, Workstation, ProductionLine, Staff
from .serializers import (
    CompanySerializer, ProductSerializer, WorkstationSerializer,
    ProductionLineSerializer, StaffSerializer
)


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['active']
    search_fields = ['number', 'name', 'email']
    ordering_fields = ['number', 'name', 'created_at']


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['active', 'global_type_of_material', 'entity_type']
    search_fields = ['number', 'name', 'ean', 'external_number']
    ordering_fields = ['number', 'name', 'created_at']


class WorkstationViewSet(viewsets.ModelViewSet):
    queryset = Workstation.objects.all()
    serializer_class = WorkstationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['active', 'production_line']
    search_fields = ['number', 'name']
    ordering_fields = ['number', 'name']


class ProductionLineViewSet(viewsets.ModelViewSet):
    queryset = ProductionLine.objects.all()
    serializer_class = ProductionLineSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['active']
    search_fields = ['number', 'name']
    ordering_fields = ['number', 'name']


class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['active']
    search_fields = ['number', 'name', 'surname', 'email']
    ordering_fields = ['number', 'surname', 'name']
