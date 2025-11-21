from rest_framework.routers import DefaultRouter
from .views import MaterialStockViewSet, ContainerViewSet, TraceabilityRecordViewSet, KanbanCardViewSet

router = DefaultRouter()
router.register(r'stock', MaterialStockViewSet)
router.register(r'containers', ContainerViewSet)
router.register(r'traceability', TraceabilityRecordViewSet)
router.register(r'kanban', KanbanCardViewSet)

urlpatterns = router.urls
