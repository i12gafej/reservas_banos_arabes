from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('reservations.urls')),
    path('api/v1/', include('api.v1.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Servir archivos MEDIA durante el desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 