from rest_framework import serializers

from reservations.dtos.book import BookDTO, BookLogDTO, BookDetailDTO, BookMassageUpdateDTO
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
    observation = serializers.CharField(required=False, allow_blank=True)

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
    observation = serializers.CharField(required=False, allow_blank=True)

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

    # Campos de masajes para edición
    massage60Relax = serializers.IntegerField(min_value=0, default=0, required=False)
    massage60Piedra = serializers.IntegerField(min_value=0, default=0, required=False)
    massage60Exfol = serializers.IntegerField(min_value=0, default=0, required=False)
    massage30Relax = serializers.IntegerField(min_value=0, default=0, required=False)
    massage30Piedra = serializers.IntegerField(min_value=0, default=0, required=False)
    massage30Exfol = serializers.IntegerField(min_value=0, default=0, required=False)
    massage15Relax = serializers.IntegerField(min_value=0, default=0, required=False)

    def update(self, instance, validated_data):
        """Actualiza una reserva y genera log automático. También compara y actualiza masajes si hay cambios."""
        # Extraer comentario de log personalizado si se proporciona
        log_comment = validated_data.pop('log_comment', None)
        
        # Extraer datos de masajes del validated_data
        massage_fields = ['massage60Relax', 'massage60Piedra', 'massage60Exfol', 
                         'massage30Relax', 'massage30Piedra', 'massage30Exfol', 'massage15Relax']
        
        massage_data = {}
        for field in massage_fields:
            if field in validated_data:
                massage_data[field] = validated_data.pop(field)
        
        # Obtener el número de personas para los masajes
        people = validated_data.get('people', instance.people)
        
        # VALIDACIÓN: Verificar que hay suficientes baños para todas las personas
        if massage_data:
            total_baths = sum(massage_data.values())
            
            # Si hay masajes, verificar que el total de baños no sea menor que personas
            if total_baths > 0 and people < total_baths:
                raise serializers.ValidationError(f"Hay menos personas ({people}) que baños reservados ({total_baths})"
                )
        
        # Primero comparar y actualizar masajes si hay cambios
        massages_updated = False
        updated_values = {}
        if massage_data:
            massages_updated, updated_values = BookManager.compare_and_update_massages(
                book_id=instance.id,
                new_massage_data=massage_data,
                people=people
            )
        
        # Filtrar solo los campos que pertenecen al BookDTO (excluyendo campos de masajes)
        book_dto_fields = {
            'booking_date', 'hour', 'people', 'comment', 'observation',
            'amount_paid', 'amount_pending', 'payment_date', 
            'checked_in', 'checked_out', 'product_id'
        }
        
        filtered_data = {k: v for k, v in validated_data.items() if k in book_dto_fields}
        
        # CRITICAL FIX: Si se actualizaron masajes, usar los valores reales de la BD
        if massages_updated and updated_values:
            # Usar los valores que realmente se guardaron en la BD
            filtered_data['product_id'] = updated_values['product_id']
            filtered_data['amount_pending'] = updated_values['amount_pending']
        
        # Solo actualizar otros campos si hay cambios en campos no relacionados con masajes
        if filtered_data:
            dto = BookDTO(id=instance.id, **filtered_data)
            dto.validate_for_update()
            
            # Usar el método que genera log automático
            BookManager.update_booking_with_log(dto, log_comment)
        
        # Retornar los detalles completos actualizados
        return BookManager.get_book_detail(instance.id)


class BookMassageUpdateSerializer(serializers.Serializer):
    """Serializer para actualizar masajes de una reserva existente."""
    massage60Relax = serializers.IntegerField(min_value=0, default=0)
    massage60Piedra = serializers.IntegerField(min_value=0, default=0)
    massage60Exfol = serializers.IntegerField(min_value=0, default=0)
    massage30Relax = serializers.IntegerField(min_value=0, default=0)
    massage30Piedra = serializers.IntegerField(min_value=0, default=0)
    massage30Exfol = serializers.IntegerField(min_value=0, default=0)
    massage15Relax = serializers.IntegerField(min_value=0, default=0)
    people = serializers.IntegerField(min_value=1, required=True)

    def update(self, instance, validated_data):
        """Actualiza los masajes de una reserva."""
        # Crear DTO con los valores de masajes (sin precio)
        massage_dto = BookMassageUpdateDTO(**validated_data)
        
        # Actualizar los masajes usando el manager (sin pasar precio)
        updated_detail = BookManager.update_booking_massages(
            book_id=instance.id,
            massages=massage_dto
        )
        
        return updated_detail