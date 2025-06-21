from rest_framework import status, viewsets
from rest_framework.response import Response

from api.v1.serializers.availability import AvailabilitySerializer, AvailabilityRangeSerializer
from reservations.models import Availability
from reservations.managers.availability import AvailabilityManager


class AvailabilityViewSet(viewsets.ViewSet):
    """Endpoints CRUD para disponibilidad y rangos."""

    # ------------------------------------------------------------------
    # Helper de representación
    # ------------------------------------------------------------------

    @staticmethod
    def _model_to_payload(av: Availability) -> dict:
        ranges = av.availabilityrange_set.all()
        ranges_payload = [
            {
                "initial_time": r.initial_time,
                "end_time": r.end_time,
                "massagists_availability": r.massagists_availability,
            }
            for r in ranges
        ]
        return {
            "id": av.id,
            "type": av.type,
            "punctual_day": av.punctual_day,
            "weekday": av.weekday,
            "ranges": ranges_payload,
        }

    # ------------------------------------------------------------------
    # Listar
    # ------------------------------------------------------------------

    def list(self, request):
        availabilities = Availability.objects.prefetch_related("availabilityrange_set").all()
        payload = [self._model_to_payload(a) for a in availabilities]
        serializer = AvailabilitySerializer(payload, many=True)
        return Response(serializer.data)

    # ------------------------------------------------------------------
    # Crear
    # ------------------------------------------------------------------

    def create(self, request):
        serializer = AvailabilitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created = serializer.save()
        output = AvailabilitySerializer(self._model_to_payload(created)).data
        return Response(output, status=status.HTTP_201_CREATED)

    # ------------------------------------------------------------------
    # Retrieve
    # ------------------------------------------------------------------

    def retrieve(self, request, pk=None):
        try:
            av = Availability.objects.prefetch_related("availabilityrange_set").get(id=pk)
        except Availability.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = AvailabilitySerializer(self._model_to_payload(av))
        return Response(serializer.data)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, request, pk=None):
        try:
            av = Availability.objects.get(id=pk)
        except Availability.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = AvailabilitySerializer(av, data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        output = AvailabilitySerializer(self._model_to_payload(updated)).data
        return Response(output)

    # ------------------------------------------------------------------
    # Destroy
    # ------------------------------------------------------------------

    def destroy(self, request, pk=None):
        Availability.objects.filter(id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
