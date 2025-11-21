from rest_framework.routers import DefaultRouter
from .views import InspectionConfigViewSet, QualityCheckViewSet, NCRViewSet, SPCDataViewSet

router = DefaultRouter()
router.register(r'inspection-config', InspectionConfigViewSet)
router.register(r'checks', QualityCheckViewSet)
router.register(r'ncr', NCRViewSet)
router.register(r'spc', SPCDataViewSet)

urlpatterns = router.urls
