from django.urls import path, include

urlpatterns = [
    path('basic/', include('mes.plugins.basic.api.urls')),
    path('routing/', include('mes.plugins.routing.api.urls')),
    path('orders/', include('mes.plugins.orders.api.urls')),
    path('deliveries/', include('mes.plugins.deliveries.api.urls')),
    path('production-counting/', include('mes.plugins.production_counting.api.urls')),
    path('scheduling/', include('mes.plugins.scheduling.api.urls')),
    path('inventory/', include('mes.plugins.inventory.api.urls')),
    path('maintenance/', include('mes.plugins.maintenance.api.urls')),
    path('quality/', include('mes.plugins.quality.api.urls')),
]
