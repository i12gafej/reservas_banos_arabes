from rest_framework import status, viewsets
from rest_framework.response import Response

from api.v1.serializers.agent import AgentSerializer
from reservations.managers.agent import AgentManager


class AgentViewSet(viewsets.ViewSet):
    """CRUD endpoints para agentes."""

    def list(self, request):
        dtos = AgentManager.list_agents()
        serializer = AgentSerializer(dtos, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = AgentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dto_created = serializer.save()
        return Response(AgentSerializer(dto_created).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        dto = next((a for a in AgentManager.list_agents() if str(a.id) == str(pk)), None)
        if dto is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(AgentSerializer(dto).data)

    def update(self, request, pk=None):
        dto_current = next((a for a in AgentManager.list_agents() if str(a.id) == str(pk)), None)
        if dto_current is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = AgentSerializer(dto_current, data=request.data)
        serializer.is_valid(raise_exception=True)
        dto_updated = serializer.save()
        return Response(AgentSerializer(dto_updated).data)

    def destroy(self, request, pk=None):
        AgentManager.delete_agent(int(pk))
        return Response(status=status.HTTP_204_NO_CONTENT)
