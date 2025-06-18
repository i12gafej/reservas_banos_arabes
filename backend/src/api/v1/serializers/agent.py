from rest_framework import serializers

from reservations.dtos.agent import AgentDTO
from reservations.managers.agent import AgentManager


class AgentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    platform = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True, allow_null=True)

    # Creación -------------------------------------------------------------
    def create(self, validated_data):
        dto = AgentDTO(**validated_data)
        dto.validate_for_create()
        return AgentManager.create_agent(dto)

    # Actualización --------------------------------------------------------
    def update(self, instance, validated_data):
        dto = AgentDTO(id=instance.id, **validated_data)
        dto.validate_for_update()
        return AgentManager.update_agent(dto) 