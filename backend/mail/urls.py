from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MailViewSet

router = DefaultRouter()
router.register(r'mails', MailViewSet, basename='mails')

urlpatterns = [
    path('', include(router.urls)),
]