from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.v1.views.client import ClientViewSet
from api.v1.views.admin import AdminViewSet
from api.v1.views.agent import AgentViewSet
from api.v1.views.availability import AvailabilityViewSet
from api.v1.views.product import ProductViewSet
from api.v1.views.book import BookViewSet
from api.v1.views.gift_voucher import GiftVoucherViewSet

router = DefaultRouter()
router.register(r'clientes', ClientViewSet, basename='client')
router.register(r'admins', AdminViewSet, basename='admin')
router.register(r'agentes', AgentViewSet, basename='agent')
router.register(r'disponibilidades', AvailabilityViewSet, basename='availability')
router.register(r'productos', ProductViewSet, basename='product')
router.register(r'reservas', BookViewSet, basename='booking')
router.register(r'cheques', GiftVoucherViewSet, basename='gift-voucher')

urlpatterns = [
    path('', include(router.urls)),
] 