from rest_framework.routers import DefaultRouter
from .views import MaintenanceLogViewSet

router = DefaultRouter()
router.register(r'logs', MaintenanceLogViewSet)

urlpatterns = router.urls
