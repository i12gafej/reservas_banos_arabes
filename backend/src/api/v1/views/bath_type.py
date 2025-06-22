from rest_framework import status, viewsets
from rest_framework.response import Response

from api.v1.serializers.bath_type import BathTypeSerializer
from reservations.models import BathType
from reservations.managers.product import ProductManager


class BathTypeViewSet(viewsets.ViewSet):
    """Endpoints de sólo lectura + actualización de precio para BathType."""

    def list(self, request):
        bath_types = ProductManager.list_bath_types()
        serializer = BathTypeSerializer(bath_types, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            bath_type = BathType.objects.get(id=pk)
        except BathType.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(BathTypeSerializer(bath_type).data)

    def update(self, request, pk=None):
        try:
            bath_type = BathType.objects.get(id=pk)
        except BathType.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = BathTypeSerializer(bath_type, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        return Response(BathTypeSerializer(updated).data)

    # Permitir PATCH para actualizar solo precio
    def partial_update(self, request, pk=None):
        try:
            bath_type = BathType.objects.get(id=pk)
        except BathType.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = BathTypeSerializer(bath_type, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        return Response(BathTypeSerializer(updated).data) 