from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TechnologyViewSet, OperationViewSet, TechnologyOperationComponentViewSet,
    OperationProductInComponentViewSet, OperationProductOutComponentViewSet
)

router = DefaultRouter()
router.register(r'routings', TechnologyViewSet)
router.register(r'operations', OperationViewSet)
router.register(r'routing-operations', TechnologyOperationComponentViewSet)
router.register(r'operation-inputs', OperationProductInComponentViewSet)
router.register(r'operation-outputs', OperationProductOutComponentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
