from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from datetime import date

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

    # ------------------------------------------------------------------
    # Nuevos endpoints para el sistema de versionado
    # ------------------------------------------------------------------

    @action(detail=False, methods=["get"], url_path="history/(?P<target_date>[^/.]+)")
    def history(self, request, target_date=None):
        """Obtiene el historial completo de disponibilidades para un día específico."""
        try:
            # Convertir la fecha del parámetro
            target_day = date.fromisoformat(target_date)
            history = AvailabilityManager.get_availability_history_for_day(target_day)
            return Response(history)
        except ValueError:
            return Response(
                {"detail": "Formato de fecha inválido. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": f"Error al obtener historial: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["get"], url_path="by-id/(?P<availability_id>[^/.]+)")
    def by_id(self, request, availability_id=None):
        """Obtiene una disponibilidad específica por ID."""
        try:
            availability = AvailabilityManager.get_availability_by_id(int(availability_id))
            if availability is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            return Response(availability)
        except ValueError:
            return Response(
                {"detail": "ID inválido"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": f"Error al obtener disponibilidad: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["post"], url_path="create-version")
    def create_version(self, request):
        """Crea una nueva versión de disponibilidad para un día específico."""
        try:
            target_date_str = request.data.get("target_date")
            ranges_data = request.data.get("ranges", [])
            effective_date_str = request.data.get("effective_date")
            
            if not target_date_str:
                return Response(
                    {"detail": "Se requiere target_date"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Convertir fechas
            target_day = date.fromisoformat(target_date_str)
            effective_date = None
            if effective_date_str:
                effective_date = date.fromisoformat(effective_date_str)
            
            # Convertir rangos a DTOs
            from reservations.dtos.availability import AvailabilityRangeDTO
            ranges = []
            for r in ranges_data:
                ranges.append(AvailabilityRangeDTO(
                    initial_time=r["initial_time"],
                    end_time=r["end_time"],
                    massagists_availability=r["massagists_availability"]
                ))
            
            # Crear nueva versión
            new_availability = AvailabilityManager.create_new_availability_version(
                target_day, ranges, effective_date
            )
            
            # Devolver la disponibilidad creada
            output = AvailabilitySerializer(self._model_to_payload(new_availability)).data
            return Response(output, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response(
                {"detail": f"Error en formato de datos: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": f"Error al crear nueva versión: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
