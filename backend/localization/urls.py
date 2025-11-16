from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LocalizationViewSet

router = DefaultRouter()
router.register(r'localizations', LocalizationViewSet, basename='localizations')

urlpatterns = [
    path('', include(router.urls)),
]