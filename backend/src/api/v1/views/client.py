from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from api.v1.serializers.client import ClientSerializer
from reservations.managers.client import ClientManager


class ClientViewSet(viewsets.ViewSet):
    """Endpoints CRUD para clientes usando DTO/Manager."""

    def list(self, request):
        dtos = ClientManager.list_clients().clients
        serializer = ClientSerializer(dtos, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = ClientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dto_created = serializer.save()
        return Response(ClientSerializer(dto_created).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        # Reutilizar manager list + filter para simplicidad
        dto = next((c for c in ClientManager.list_clients().clients if str(c.id) == str(pk)), None)
        if dto is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(ClientSerializer(dto).data)

    def update(self, request, pk=None):
        dto_current = next((c for c in ClientManager.list_clients().clients if str(c.id) == str(pk)), None)
        if dto_current is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ClientSerializer(dto_current, data=request.data)
        serializer.is_valid(raise_exception=True)
        dto_updated = serializer.save()
        return Response(ClientSerializer(dto_updated).data)

    def destroy(self, request, pk=None):
        ClientManager.delete_client(int(pk))
        return Response(status=status.HTTP_204_NO_CONTENT) 