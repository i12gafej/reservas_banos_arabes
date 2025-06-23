from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from api.v1.serializers.product import ProductSerializer
from api.v1.serializers.bath_type import BathTypeSerializer
from reservations.models import Product
from reservations.managers.product import ProductManager


class ProductViewSet(viewsets.ViewSet):
    """CRUD endpoints para productos."""

    def list(self, request):
        products = Product.objects.all().prefetch_related("baths", "hostings")
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        try:
            product = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(ProductSerializer(product).data)

    def update(self, request, pk=None):
        try:
            product = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        return Response(ProductSerializer(updated).data)

    def destroy(self, request, pk=None):
        ProductManager.delete_product(int(pk))
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def baths(self, request, pk=None):
        """Obtiene los tipos de baño asociados a un producto."""
        try:
            product = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        # Obtener los tipos de baño a través de ProductBaths
        product_baths = product.baths.all().select_related('bath_type')
        bath_types = [pb.bath_type for pb in product_baths]
        
        serializer = BathTypeSerializer(bath_types, many=True)
        return Response(serializer.data)
