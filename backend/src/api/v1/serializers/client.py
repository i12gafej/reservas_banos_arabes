from rest_framework import serializers

from reservations.dtos.client import ClientDTO
from reservations.managers.client import ClientManager


class ClientSerializer(serializers.Serializer):
    """Serializer para listar/retornar clientes."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    surname = serializers.CharField(allow_blank=True, required=False)
    phone_number = serializers.CharField(allow_blank=True, required=False)
    email = serializers.EmailField(allow_null=True, required=False)
    created_at = serializers.DateTimeField(read_only=True)

    # ------------------------------------------------------------------
    # Creación
    # ------------------------------------------------------------------

    def create(self, validated_data):
        dto = ClientDTO(**validated_data)
        dto.validate_for_create()
        return ClientManager.create_client(dto)

    # ------------------------------------------------------------------
    # Actualización
    # ------------------------------------------------------------------

    def update(self, instance, validated_data):
        # Construir DTO de actualización
        dto = ClientDTO(id=instance.id, **validated_data)
        dto.validate_for_update()
        return ClientManager.update_client(dto) 