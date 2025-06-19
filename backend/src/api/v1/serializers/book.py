from rest_framework import serializers

from reservations.dtos.book import BookDTO, ProductInBookDTO
from reservations.managers.book import BookManager


class ProductInBookSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    availability_id = serializers.IntegerField(required=False, allow_null=True)

    def to_dto(self):
        return ProductInBookDTO(**self.validated_data)


class BookingSerializer(serializers.Serializer):
    # Solo lectura
    id = serializers.IntegerField(read_only=True)
    internal_order_id = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    # Datos básicos
    booking_date = serializers.DateTimeField()
    people = serializers.IntegerField(min_value=1, default=1)
    comment = serializers.CharField(required=False, allow_blank=True)

    amount_paid = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, default="0")
    amount_pending = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, default="0")

    payment_date = serializers.DateTimeField(required=False, allow_null=True)
    checked_in = serializers.BooleanField(required=False, allow_null=True)
    checked_out = serializers.BooleanField(required=False, allow_null=True)

    client_id = serializers.IntegerField()

    products = ProductInBookSerializer(many=True)

    # ------------------------------------------------------------------
    # Creación
    # ------------------------------------------------------------------

    def create(self, validated_data):
        products_data = validated_data.pop("products")
        product_dtos = [ProductInBookDTO(**p) for p in products_data]
        dto = BookDTO(products=product_dtos, **validated_data)
        dto.validate_for_create()
        booking_dto = BookManager.create_booking(dto)
        return booking_dto  # devuelve DTO para coherencia con otros serializers

    # ------------------------------------------------------------------
    # Actualización
    # ------------------------------------------------------------------

    def update(self, instance, validated_data):
        products_data = validated_data.pop("products", None)
        product_dtos = None
        if products_data is not None:
            product_dtos = [ProductInBookDTO(**p) for p in products_data]

        dto_kwargs = {**validated_data}
        if product_dtos is not None:
            dto_kwargs["products"] = product_dtos

        dto = BookDTO(id=instance.id, **dto_kwargs)  # type: ignore
        dto.validate_for_update()
        updated_dto = BookManager.update_booking(dto)
        return updated_dto 