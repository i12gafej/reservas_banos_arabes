from rest_framework import serializers
from reservations.models import Constraint, ConstraintRange


class ConstraintRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstraintRange
        fields = ['initial_time', 'end_time']


class ConstraintSerializer(serializers.ModelSerializer):
    ranges = ConstraintRangeSerializer(many=True, source='constraintrange_set')
    
    class Meta:
        model = Constraint
        fields = ['id', 'day', 'created_at', 'ranges']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        ranges_data = validated_data.pop('constraintrange_set', [])
        constraint = Constraint.objects.create(**validated_data)
        
        for range_data in ranges_data:
            ConstraintRange.objects.create(
                constraint=constraint,
                **range_data
            )
        
        return constraint

    def update(self, instance, validated_data):
        ranges_data = validated_data.pop('constraintrange_set', [])
        
        # Actualizar campos del constraint
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Eliminar rangos existentes y crear nuevos
        instance.constraintrange_set.all().delete()
        for range_data in ranges_data:
            ConstraintRange.objects.create(
                constraint=instance,
                **range_data
            )
        
        return instance 