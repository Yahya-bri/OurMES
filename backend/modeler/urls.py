from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ModelerViewSet

router = DefaultRouter()
router.register(r'modelers', ModelerViewSet, basename='modelers')

urlpatterns = [
    path('', include(router.urls)),
]