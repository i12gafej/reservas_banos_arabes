from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('reservations.urls')),  # Incluimos las URLs de la aplicación reservations
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 