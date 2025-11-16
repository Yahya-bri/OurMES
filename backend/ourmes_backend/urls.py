from django.urls import path, include

urlpatterns = [
    path('api/', include([
        path('commons/', include('commons.urls')),
        path('localization/', include('localization.urls')),
        path('mail/', include('mail.urls')),
        path('modeler/', include('modeler.urls')),
        path('report/', include('report.urls')),
        path('security/', include('security.urls')),
        path('swagger/', include('swagger.urls')),
        path('tenant/', include('tenant.urls')),
        path('mes/', include('mes.urls')),
    ])),
]
