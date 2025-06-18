from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExampleViewSet

router = DefaultRouter()
router.register(r'example', ExampleViewSet, basename='example')

urlpatterns = [
    path('', include(router.urls)),
] 