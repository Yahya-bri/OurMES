from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductionCountingViewSet

router = DefaultRouter()
router.register(r'production-counting', ProductionCountingViewSet, basename='production-counting')

urlpatterns = [
    path('', include(router.urls)),
]