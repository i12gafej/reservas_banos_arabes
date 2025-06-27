from rest_framework import serializers

from reservations.dtos.gift_voucher import GiftVoucherDTO, GiftVoucherWithDetailsDTO, StaffGiftVoucherPayloadDTO
from reservations.dtos.book import StaffBathRequestDTO
from reservations.managers.gift_voucher import GiftVoucherManager


class GiftVoucherSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    code = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    price = serializers.DecimalField(max_digits=8, decimal_places=2)
    buyer_client_id = serializers.IntegerField()
    product_id = serializers.IntegerField()

    used = serializers.BooleanField(required=False, default=False)
    status = serializers.CharField(required=False, allow_blank=True)
    payment_date = serializers.DateTimeField(required=False, allow_null=True)
    people = serializers.IntegerField(required=False, min_value=1)

    recipients_email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    recipients_name = serializers.CharField(required=False, allow_blank=True)
    recipients_surname = serializers.CharField(required=False, allow_blank=True)
    gift_name = serializers.CharField(required=False, allow_blank=True)
    gift_description = serializers.CharField(required=False, allow_blank=True)

    # ------------------------------------------------------------------
    # Creación
    # ------------------------------------------------------------------

    def create(self, validated_data):
        dto = GiftVoucherDTO(**validated_data)
        dto.validate_for_create()
        voucher_dto = GiftVoucherManager.create_voucher(dto)
        return voucher_dto

    # ------------------------------------------------------------------
    # Actualización
    # ------------------------------------------------------------------

    def update(self, instance, validated_data):
        dto = GiftVoucherDTO(id=instance.id, **validated_data)
        dto.validate_for_update()
        updated = GiftVoucherManager.update_voucher(dto)
        return updated


class GiftVoucherWithDetailsSerializer(serializers.Serializer):
    """Serializer para mostrar cheques regalo con detalles completos."""
    id = serializers.IntegerField(read_only=True)
    code = serializers.CharField(read_only=True)
    price = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    used = serializers.BooleanField(read_only=True)
    status = serializers.CharField(read_only=True)
    payment_date = serializers.DateTimeField(read_only=True)
    people = serializers.IntegerField(read_only=True)
    buyer_client_id = serializers.IntegerField(read_only=True)
    product_id = serializers.IntegerField(read_only=True)
    recipients_email = serializers.CharField(read_only=True)
    recipients_name = serializers.CharField(read_only=True)
    recipients_surname = serializers.CharField(read_only=True)
    gift_name = serializers.CharField(read_only=True)
    gift_description = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    bought_date = serializers.DateTimeField(read_only=True)
    
    # Información del cliente comprador
    buyer_name = serializers.CharField(read_only=True)
    buyer_surname = serializers.CharField(read_only=True)
    buyer_phone = serializers.CharField(read_only=True)
    buyer_email = serializers.CharField(read_only=True)
    buyer_client_created_at = serializers.DateTimeField(read_only=True)
    
    # Información del producto
    product_name = serializers.CharField(read_only=True)


# ------------------------------------------------------------------
# Serializer para masajes
# ------------------------------------------------------------------

class StaffBathRequestSerializer(serializers.Serializer):
    massage_type = serializers.CharField()
    minutes = serializers.CharField()
    quantity = serializers.IntegerField(min_value=0)

    def to_dto(self):
        return StaffBathRequestDTO(**self.validated_data)


# ------------------------------------------------------------------
# Serializer para crear cheques regalo desde staff
# ------------------------------------------------------------------

class StaffGiftVoucherSerializer(serializers.Serializer):
    # Datos del comprador
    buyer_name = serializers.CharField(max_length=255)
    buyer_surname = serializers.CharField(max_length=255, required=False, allow_blank=True)
    buyer_phone = serializers.CharField(max_length=50, required=False, allow_blank=True)
    buyer_email = serializers.EmailField()
    
    # Datos del destinatario (opcionales)
    recipient_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    recipient_surname = serializers.CharField(max_length=255, required=False, allow_blank=True)
    recipient_email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    
    # Datos del cheque regalo
    gift_name = serializers.CharField(max_length=255)
    gift_description = serializers.CharField(required=False, allow_blank=True)
    people = serializers.IntegerField(min_value=1)
    
    # Masajes
    baths = StaffBathRequestSerializer(many=True)
    
    # Otros
    send_whatsapp_buyer = serializers.BooleanField(required=False, default=False)

    def validate(self, data):
        """Validar que la cantidad de masajes no exceda el número de personas."""
        people = data.get('people')
        baths_data = data.get('baths', [])
        
        if people and baths_data:
            total_baths = sum(
                bath['quantity'] for bath in baths_data 
                if bath.get('massage_type') != 'none'
            )
            
            if total_baths > people:
                raise serializers.ValidationError(
                    f"Hay más masajes ({total_baths}) que personas ({people}). "
                    f"Reduce la cantidad de masajes o aumenta el número de personas."
                )
        
        return data

    def create(self, validated_data):
        # Convertir baths de dict a DTOs
        baths_data = validated_data.pop('baths', [])
        bath_dtos = []
        for bath_data in baths_data:
            bath_serializer = StaffBathRequestSerializer(data=bath_data)
            bath_serializer.is_valid(raise_exception=True)
            bath_dtos.append(bath_serializer.to_dto())
        
        # Crear payload DTO
        payload = StaffGiftVoucherPayloadDTO(
            baths=bath_dtos,
            **validated_data
        )
        
        # Crear cheque regalo
        voucher_dto = GiftVoucherManager.create_gift_voucher_from_staff(payload)
        return voucher_dto 
        dto = GiftVoucherDTO(id=instance.id, **validated_data)
        dto.validate_for_update()
        updated = GiftVoucherManager.update_voucher(dto)
        return updated


class GiftVoucherWithDetailsSerializer(serializers.Serializer):
    """Serializer para mostrar cheques regalo con detalles completos."""
    id = serializers.IntegerField(read_only=True)
    code = serializers.CharField(read_only=True)
    price = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    used = serializers.BooleanField(read_only=True)
    status = serializers.CharField(read_only=True)
    payment_date = serializers.DateTimeField(read_only=True)
    people = serializers.IntegerField(read_only=True)
    buyer_client_id = serializers.IntegerField(read_only=True)
    product_id = serializers.IntegerField(read_only=True)
    recipients_email = serializers.CharField(read_only=True)
    recipients_name = serializers.CharField(read_only=True)
    recipients_surname = serializers.CharField(read_only=True)
    gift_name = serializers.CharField(read_only=True)
    gift_description = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    bought_date = serializers.DateTimeField(read_only=True)
    
    # Información del cliente comprador
    buyer_name = serializers.CharField(read_only=True)
    buyer_surname = serializers.CharField(read_only=True)
    buyer_phone = serializers.CharField(read_only=True)
    buyer_email = serializers.CharField(read_only=True)
    buyer_client_created_at = serializers.DateTimeField(read_only=True)
    
    # Información del producto
    product_name = serializers.CharField(read_only=True)


# ------------------------------------------------------------------
# Serializer para masajes
# ------------------------------------------------------------------

class StaffBathRequestSerializer(serializers.Serializer):
    massage_type = serializers.CharField()
    minutes = serializers.CharField()
    quantity = serializers.IntegerField(min_value=0)

    def to_dto(self):
        return StaffBathRequestDTO(**self.validated_data)


# ------------------------------------------------------------------
# Serializer para crear cheques regalo desde staff
# ------------------------------------------------------------------

class StaffGiftVoucherSerializer(serializers.Serializer):
    # Datos del comprador
    buyer_name = serializers.CharField(max_length=255)
    buyer_surname = serializers.CharField(max_length=255, required=False, allow_blank=True)
    buyer_phone = serializers.CharField(max_length=50, required=False, allow_blank=True)
    buyer_email = serializers.EmailField()
    
    # Datos del destinatario (opcionales)
    recipient_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    recipient_surname = serializers.CharField(max_length=255, required=False, allow_blank=True)
    recipient_email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    
    # Datos del cheque regalo
    gift_name = serializers.CharField(max_length=255)
    gift_description = serializers.CharField(required=False, allow_blank=True)
    people = serializers.IntegerField(min_value=1)
    
    # Masajes
    baths = StaffBathRequestSerializer(many=True)
    
    # Otros
    send_whatsapp_buyer = serializers.BooleanField(required=False, default=False)

    def validate(self, data):
        """Validar que la cantidad de masajes no exceda el número de personas."""
        people = data.get('people')
        baths_data = data.get('baths', [])
        
        if people and baths_data:
            total_baths = sum(
                bath['quantity'] for bath in baths_data 
                if bath.get('massage_type') != 'none'
            )
            
            if total_baths > people:
                raise serializers.ValidationError(
                    f"Hay más masajes ({total_baths}) que personas ({people}). "
                    f"Reduce la cantidad de masajes o aumenta el número de personas."
                )
        
        return data

    def create(self, validated_data):
        # Convertir baths de dict a DTOs
        baths_data = validated_data.pop('baths', [])
        bath_dtos = []
        for bath_data in baths_data:
            bath_serializer = StaffBathRequestSerializer(data=bath_data)
            bath_serializer.is_valid(raise_exception=True)
            bath_dtos.append(bath_serializer.to_dto())
        
        # Crear payload DTO
        payload = StaffGiftVoucherPayloadDTO(
            baths=bath_dtos,
            **validated_data
        )
        
        # Crear cheque regalo
        voucher_dto = GiftVoucherManager.create_gift_voucher_from_staff(payload)
        return voucher_dto 