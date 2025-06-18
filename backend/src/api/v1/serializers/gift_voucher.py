from rest_framework import serializers

from reservations.dtos.gift_voucher import GiftVoucherDTO, GiftProductQuantityDTO
from reservations.managers.gift_voucher import GiftVoucherManager  # suponemos su existencia


class GiftProductQuantitySerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def to_dto(self):
        return GiftProductQuantityDTO(**self.validated_data)


class GiftVoucherSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    code = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    price = serializers.DecimalField(max_digits=8, decimal_places=2)
    buyer_client_id = serializers.IntegerField()

    used = serializers.BooleanField(required=False, default=False)

    recipients_email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    recipients_name = serializers.CharField(required=False, allow_blank=True)
    recipients_surname = serializers.CharField(required=False, allow_blank=True)
    gift_name = serializers.CharField(required=False, allow_blank=True)
    gift_description = serializers.CharField(required=False, allow_blank=True)

    products = GiftProductQuantitySerializer(many=True)

    # ------------------------------------------------------------------
    # Creación
    # ------------------------------------------------------------------

    def create(self, validated_data):
        products_data = validated_data.pop("products")
        product_dtos = [GiftProductQuantityDTO(**p) for p in products_data]
        dto = GiftVoucherDTO(products=product_dtos, **validated_data)
        dto.validate_for_create()
        voucher_dto = GiftVoucherManager.create_voucher(dto)
        return voucher_dto

    # ------------------------------------------------------------------
    # Actualización
    # ------------------------------------------------------------------

    def update(self, instance, validated_data):
        products_data = validated_data.pop("products", None)
        product_dtos = None
        if products_data is not None:
            product_dtos = [GiftProductQuantityDTO(**p) for p in products_data]

        dto_kwargs = {**validated_data}
        if product_dtos is not None:
            dto_kwargs["products"] = product_dtos

        dto = GiftVoucherDTO(id=instance.id, **dto_kwargs)
        dto.validate_for_update()
        updated = GiftVoucherManager.update_voucher(dto)
        return updated 