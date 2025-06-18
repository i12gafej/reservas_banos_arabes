from rest_framework import status, viewsets
from rest_framework.response import Response

from api.v1.serializers.product import ProductSerializer
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
