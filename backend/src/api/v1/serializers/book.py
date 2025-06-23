from rest_framework import serializers

from reservations.dtos.book import BookDTO
from reservations.managers.book import BookManager


class BookingSerializer(serializers.Serializer):
    # Solo lectura
    id = serializers.IntegerField(read_only=True)
    internal_order_id = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    # Datos básicos
    booking_date = serializers.DateField()
    hour = serializers.TimeField(required=False)
    people = serializers.IntegerField(min_value=1, default=1)
    comment = serializers.CharField(required=False, allow_blank=True)

    amount_paid = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, default="0")
    amount_pending = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, default="0")

    payment_date = serializers.DateTimeField(required=False, allow_null=True)
    checked_in = serializers.BooleanField(required=False, allow_null=True)
    checked_out = serializers.BooleanField(required=False, allow_null=True)

    client_id = serializers.IntegerField()
    product_id = serializers.IntegerField()

    # ------------------------------------------------------------------
    # Creación
    # ------------------------------------------------------------------

    def create(self, validated_data):
        dto = BookDTO(**validated_data)
        dto.validate_for_create()
        booking_dto = BookManager.create_booking(dto)
        return booking_dto  # devuelve DTO para coherencia con otros serializers

    # ------------------------------------------------------------------
    # Actualización
    # ------------------------------------------------------------------

    def update(self, instance, validated_data):
        dto = BookDTO(id=instance.id, **validated_data)  # type: ignore
        dto.validate_for_update()
        updated_dto = BookManager.update_booking(dto)
        return updated_dto 