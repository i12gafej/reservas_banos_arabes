from rest_framework import serializers

from reservations.dtos.admin import AdminDTO
from reservations.managers.admin import AdminManager


class AdminSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    surname = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)

    # Creación -------------------------------------------------------------
    def create(self, validated_data):
        dto = AdminDTO(**validated_data)
        dto.validate_for_create()
        return AdminManager.create_admin(dto)

    # Actualización --------------------------------------------------------
    def update(self, instance, validated_data):
        dto = AdminDTO(id=instance.id, **validated_data)
        dto.validate_for_update()
        return AdminManager.update_admin(dto) 