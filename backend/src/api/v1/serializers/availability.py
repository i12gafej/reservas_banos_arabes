from rest_framework import serializers

from reservations.dtos.availability import AvailabilityDTO, AvailabilityRangeDTO
from reservations.managers.availability import AvailabilityManager


class AvailabilityRangeSerializer(serializers.Serializer):
    initial_time = serializers.TimeField()
    end_time = serializers.TimeField()
    massagists_availability = serializers.IntegerField(min_value=0)

    def to_dto(self):
        return AvailabilityRangeDTO(**self.validated_data)


class AvailabilitySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)

    type = serializers.ChoiceField(choices=[AvailabilityDTO.TYPE_WEEKDAY, AvailabilityDTO.TYPE_PUNCTUAL])
    punctual_day = serializers.DateField(required=False, allow_null=True)
    weekday = serializers.IntegerField(required=False, allow_null=True, min_value=1, max_value=7)

    ranges = AvailabilityRangeSerializer(many=True)

    # ------------------------------------------------------------------
    # Actualización
    # ------------------------------------------------------------------

    def create(self, validated_data):
        ranges_data = validated_data.pop("ranges")
        ranges_dtos = [AvailabilityRangeDTO(**r) for r in ranges_data]
        dto = AvailabilityDTO(ranges=ranges_dtos, **validated_data)  # type: ignore
        dto.validate()
        availability = AvailabilityManager.create_availability(dto)
        return availability

    def update(self, instance, validated_data):
        ranges_data = validated_data.pop("ranges")
        ranges_dtos = [AvailabilityRangeDTO(**r) for r in ranges_data]
        dto = AvailabilityDTO(ranges=ranges_dtos, **validated_data)  # type: ignore
        dto.validate()
        updated = AvailabilityManager.update_availability(instance.id, dto)
        return updated 