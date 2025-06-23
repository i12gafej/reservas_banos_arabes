from rest_framework import serializers

from reservations.dtos.gift_voucher import GiftVoucherDTO
from reservations.managers.gift_voucher import GiftVoucherManager


class GiftVoucherSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    code = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    price = serializers.DecimalField(max_digits=8, decimal_places=2)
    buyer_client_id = serializers.IntegerField()
    product_id = serializers.IntegerField()

    used = serializers.BooleanField(required=False, default=False)

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