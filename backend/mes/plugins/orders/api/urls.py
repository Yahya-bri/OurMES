from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderStateChangeViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet)
router.register(r'order-state-changes', OrderStateChangeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
