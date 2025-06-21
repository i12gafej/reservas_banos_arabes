from datetime import date
from typing import List, Optional

from django.db import transaction

from reservations.dtos.availability import AvailabilityDTO, AvailabilityRangeDTO
from reservations.models import Availability, AvailabilityRange


class AvailabilityManager:
    """Gestor para operaciones de Availability y AvailabilityRange."""

    # ------------------------------------------------------------------
    # Lectura
    # ------------------------------------------------------------------

    @staticmethod
    def get_ranges_for_day(target_day: date) -> List[AvailabilityRange]:
        """Devuelve la lista de rangos para un día concreto.

        - Primero busca una Availability puntual (type='punctual').
        - Si no existe, busca la Availability del día de la semana correspondiente.
        - Si no hay ninguna, devuelve lista vacía.
        """

        # 1) Availability puntual
        availability: Optional[Availability] = (
            Availability.objects
            .prefetch_related("availabilityrange_set")
            .filter(type=AvailabilityDTO.TYPE_PUNCTUAL, punctual_day=target_day)
            .first()
        )

        if availability is None:
            weekday = target_day.isoweekday()  # 1=Lunes ... 7=Domingo
            availability = (
                Availability.objects
                .prefetch_related("availabilityrange_set")
                .filter(type=AvailabilityDTO.TYPE_WEEKDAY, weekday=weekday)
                .first()
            )

        if availability is None:
            return []

        return list(availability.availabilityrange_set.all())

    # ------------------------------------------------------------------
    # Actualización
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def update_availability(avail_id: int, dto: AvailabilityDTO) -> Availability:
        """Actualiza (o transforma) una Availability y sus rangos."""

        dto.validate()
        availability: Availability = Availability.objects.get(id=avail_id)

        # Actualizar campos principales según tipo
        availability.type = dto.type
        if dto.type == AvailabilityDTO.TYPE_PUNCTUAL:
            availability.punctual_day = dto.punctual_day
            availability.weekday = None
        else:
            availability.weekday = dto.weekday
            availability.punctual_day = None
        availability.save()

        # Limpiar rangos anteriores
        AvailabilityRange.objects.filter(availability=availability).delete()

        # Crear los nuevos rangos
        AvailabilityManager._create_related_ranges(availability, dto.ranges)

        return availability

    # ------------------------------------------------------------------
    # Creación
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def create_availability(dto: AvailabilityDTO) -> Availability:
        """Crea una nueva Availability y sus rangos asociados."""

        dto.validate()

        if dto.type == AvailabilityDTO.TYPE_PUNCTUAL:
            availability = Availability.objects.create(
                type=dto.type,
                punctual_day=dto.punctual_day,
            )
        else:
            availability = Availability.objects.create(
                type=dto.type,
                weekday=dto.weekday,
            )

        AvailabilityManager._create_related_ranges(availability, dto.ranges)

        return availability

    # ------------------------------------------------------------------
    # Helper interno
    # ------------------------------------------------------------------

    @staticmethod
    def _create_related_ranges(availability: Availability, ranges_dto: List[AvailabilityRangeDTO]) -> None:
        """Crea AvailabilityRange a partir de los DTO proporcionados."""
        for r in ranges_dto:
            r.validate()
            AvailabilityRange.objects.create(
                availability=availability,
                initial_time=r.initial_time,
                end_time=r.end_time,
                massagists_availability=r.massagists_availability,
            )
