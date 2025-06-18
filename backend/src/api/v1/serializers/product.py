from rest_framework import serializers

from reservations.dtos.product import (
    ProductCreateDTO,
    BathQuantityDTO,
    HostingQuantityDTO,
)
from reservations.managers.product import ProductManager


class BathQuantitySerializer(serializers.Serializer):
    bath_type_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def to_dto(self):
        return BathQuantityDTO(
            bath_type=None,  # Sólo usamos id en manager
            quantity=self.validated_data["quantity"],
        )


class HostingQuantitySerializer(serializers.Serializer):
    hosting_type_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def to_dto(self):
        return HostingQuantityDTO(
            hosting_type=None,
            quantity=self.validated_data["quantity"],
        )


class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)

    name = serializers.CharField()
    observation = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    price = serializers.DecimalField(max_digits=8, decimal_places=2)
    uses_capacity = serializers.BooleanField(default=True)
    uses_massagist = serializers.BooleanField(default=False)
    visible = serializers.BooleanField(default=True)

    baths = BathQuantitySerializer(many=True, required=False)
    hostings = HostingQuantitySerializer(many=True, required=False)

    # ------------------------------------------------------------------
    # Creación
    # ------------------------------------------------------------------

    def create(self, validated_data):
        baths_data = validated_data.pop("baths", [])
        hostings_data = validated_data.pop("hostings", [])

        baths_dtos = [BathQuantityDTO(bath_type_id=b["bath_type_id"], quantity=b["quantity"]) for b in baths_data]  # type: ignore
        hostings_dtos = [HostingQuantityDTO(hosting_type_id=h["hosting_type_id"], quantity=h["quantity"]) for h in hostings_data]  # type: ignore

        dto = ProductCreateDTO(
            baths=baths_dtos,
            hostings=hostings_dtos,
            **validated_data,
        )
        dto.validate()
        product = ProductManager.create_product(dto)
        return product

    # ------------------------------------------------------------------
    # Actualización
    # ------------------------------------------------------------------

    def update(self, instance, validated_data):
        baths_data = validated_data.pop("baths", None)
        hostings_data = validated_data.pop("hostings", None)

        kwargs = {**validated_data}
        if baths_data is not None:
            kwargs["baths"] = [BathQuantityDTO(bath_type_id=b["bath_type_id"], quantity=b["quantity"]) for b in baths_data]  # type: ignore
        if hostings_data is not None:
            kwargs["hostings"] = [HostingQuantityDTO(hosting_type_id=h["hosting_type_id"], quantity=h["quantity"]) for h in hostings_data]  # type: ignore

        dto = ProductCreateDTO(id=instance.id, **kwargs)  # type: ignore
        product = ProductManager.update_product(instance.id, dto)
        return product 