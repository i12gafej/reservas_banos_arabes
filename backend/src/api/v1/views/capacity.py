from rest_framework import status, viewsets
from rest_framework.response import Response

from api.v1.serializers.capacity import CapacitySerializer
from reservations.models import Capacity


class CapacityViewSet(viewsets.ViewSet):
    """Endpoints GET y PUT para Capacity (aforo)."""

    # ------------------------------------------------------------------
    # Obtener listado (por si se necesita)
    # ------------------------------------------------------------------
    def list(self, request):
        cap = Capacity.objects.first()
        if not cap:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(CapacitySerializer(cap).data)

    # ------------------------------------------------------------------
    # Obtener por ID
    # ------------------------------------------------------------------
    def retrieve(self, request, pk=None):
        cap = Capacity.objects.first()
        if not cap:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(CapacitySerializer(cap).data)

    # ------------------------------------------------------------------
    # Actualizar valor aforo
    # ------------------------------------------------------------------
    def update(self, request, pk=None):
        cap = Capacity.objects.first()
        if not cap:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CapacitySerializer(cap, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
