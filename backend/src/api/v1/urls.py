from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.v1.views.client import ClientViewSet
from api.v1.views.admin import AdminViewSet
from api.v1.views.agent import AgentViewSet
from api.v1.views.availability import AvailabilityViewSet
from api.v1.views.product import ProductViewSet
from api.v1.views.book import BookViewSet
from api.v1.views.gift_voucher import GiftVoucherViewSet
from api.v1.views.capacity import CapacityViewSet
from api.v1.views.bath_type import BathTypeViewSet
from api.v1.views.constraint import ConstraintViewSet
from api.v1.views.general_search import GeneralSearchView

router = DefaultRouter()
router.register(r'clientes', ClientViewSet, basename='client')
router.register(r'admins', AdminViewSet, basename='admin')
router.register(r'agentes', AgentViewSet, basename='agent')
router.register(r'disponibilidades', AvailabilityViewSet, basename='availability')
router.register(r'productos', ProductViewSet, basename='product')
router.register(r'reservas', BookViewSet, basename='booking')
router.register(r'cheques', GiftVoucherViewSet, basename='gift-voucher')
router.register(r'capacity', CapacityViewSet, basename='capacity')
router.register(r'bath-types', BathTypeViewSet, basename='bath-type')
router.register(r'restricciones', ConstraintViewSet, basename='constraint')

urlpatterns = [
    path('', include(router.urls)),
    path('busqueda-general/', GeneralSearchView.as_view(), name='general-search'),
] 