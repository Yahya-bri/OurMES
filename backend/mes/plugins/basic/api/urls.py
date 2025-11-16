from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CompanyViewSet, ProductViewSet, WorkstationViewSet,
    ProductionLineViewSet, StaffViewSet
)

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'products', ProductViewSet)
router.register(r'workstations', WorkstationViewSet)
router.register(r'production-lines', ProductionLineViewSet)
router.register(r'staff', StaffViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
