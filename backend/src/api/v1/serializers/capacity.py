from rest_framework import serializers
from reservations.models import Capacity

class CapacitySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    value = serializers.IntegerField(min_value=1)

    # ------------------------------------------------------------------
    # Create (unlikely needed but included for completeness)
    # ------------------------------------------------------------------
    def create(self, validated_data):
        return Capacity.objects.create(**validated_data)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    def update(self, instance, validated_data):
        instance.value = validated_data["value"]
        instance.save()
        return instance
