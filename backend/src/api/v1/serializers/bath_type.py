from rest_framework import serializers

from reservations.models import BathType


class BathTypeSerializer(serializers.ModelSerializer):
    """Serializer simplificado de BathType.

    Solo permite actualizar el precio; el resto de campos son de solo lectura.
    """

    class Meta:
        model = BathType
        fields = (
            "id",
            "name",
            "massage_type",
            "massage_duration",
            "baths_duration",
            "description",
            "price",
        )
        read_only_fields = (
            "id",
            "name",
            "massage_type",
            "massage_duration",
            "baths_duration",
            "description",
        )

    def update(self, instance, validated_data):
        # Solo actualizamos el precio
        price = validated_data.get("price")
        if price is not None:
            instance.price = price
            instance.save(update_fields=["price"])
        return instance 