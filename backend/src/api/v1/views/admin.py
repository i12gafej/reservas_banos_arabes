from rest_framework import status, viewsets
from rest_framework.response import Response

from api.v1.serializers.admin import AdminSerializer
from reservations.managers.admin import AdminManager


class AdminViewSet(viewsets.ViewSet):
    """CRUD endpoints para administradores."""

    def list(self, request):
        dtos = AdminManager.list_admins()
        serializer = AdminSerializer(dtos, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = AdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dto_created = serializer.save()
        return Response(AdminSerializer(dto_created).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        dto = next((a for a in AdminManager.list_admins() if str(a.id) == str(pk)), None)
        if dto is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(AdminSerializer(dto).data)

    def update(self, request, pk=None):
        dto_current = next((a for a in AdminManager.list_admins() if str(a.id) == str(pk)), None)
        if dto_current is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = AdminSerializer(dto_current, data=request.data)
        serializer.is_valid(raise_exception=True)
        dto_updated = serializer.save()
        return Response(AdminSerializer(dto_updated).data)

    def destroy(self, request, pk=None):
        AdminManager.delete_admin(int(pk))
        return Response(status=status.HTTP_204_NO_CONTENT) 