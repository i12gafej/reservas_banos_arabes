from rest_framework import serializers

from reservations.dtos.book import BookDTO, BookLogDTO, BookDetailDTO
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


class BookLogSerializer(serializers.Serializer):
    """Serializer para logs de reservas."""
    id = serializers.IntegerField(read_only=True)
    book_id = serializers.IntegerField(required=True)
    datetime = serializers.DateTimeField(read_only=True)
    comment = serializers.CharField(required=True)

    def create(self, validated_data):
        dto = BookLogDTO(**validated_data)
        dto.validate_for_create()
        log_dto = BookManager.create_book_log(dto)
        return log_dto


class BookDetailSerializer(serializers.Serializer):
    """Serializer para detalles completos de una reserva."""
    # Campos básicos
    id = serializers.IntegerField(read_only=True)
    internal_order_id = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    
    # Datos editables básicos
    booking_date = serializers.DateField()
    hour = serializers.TimeField(required=False)
    people = serializers.IntegerField(min_value=1, default=1)
    comment = serializers.CharField(required=False, allow_blank=True)

    # Datos de pago
    amount_paid = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, default="0")
    amount_pending = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, default="0")
    payment_date = serializers.DateTimeField(required=False, allow_null=True)
    
    # Estados
    checked_in = serializers.BooleanField(required=False, allow_null=True)
    checked_out = serializers.BooleanField(required=False, allow_null=True)

    # Referencias
    client_id = serializers.IntegerField(read_only=True)
    product_id = serializers.IntegerField()

    # Información del cliente (solo lectura)
    client_name = serializers.CharField(read_only=True)
    client_surname = serializers.CharField(read_only=True)
    client_phone = serializers.CharField(read_only=True)
    client_email = serializers.CharField(read_only=True)
    client_created_at = serializers.DateTimeField(read_only=True)

    # Información del creador (solo lectura)
    creator_type_name = serializers.CharField(read_only=True)
    creator_name = serializers.CharField(read_only=True)

    # Información del producto/masajes (solo lectura)
    product_baths = serializers.ListField(read_only=True)

    def update(self, instance, validated_data):
        """Actualiza una reserva y genera log automático."""
        # Extraer comentario de log personalizado si se proporciona
        log_comment = validated_data.pop('log_comment', None)
        
        dto = BookDTO(id=instance.id, **validated_data)
        dto.validate_for_update()
        
        # Usar el método que genera log automático
        updated_dto = BookManager.update_booking_with_log(dto, log_comment)
        
        # Retornar los detalles completos actualizados
        return BookManager.get_book_detail(updated_dto.id)