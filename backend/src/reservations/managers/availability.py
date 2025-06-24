from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any

from django.db import transaction
from django.utils import timezone

from reservations.dtos.availability import AvailabilityDTO, AvailabilityRangeDTO
from reservations.models import Availability, AvailabilityRange



class AvailabilityManager:
    """Gestor para operaciones de Availability y AvailabilityRange."""

    # ------------------------------------------------------------------
    # Función auxiliar para convertir a date
    # ------------------------------------------------------------------

    @staticmethod
    def get_ranges_for_day(target_day: date) -> List[AvailabilityRange]:
        """Devuelve la lista de rangos para un día concreto.

        - Primero busca una Availability puntual (type='punctual').
        - Si no existe, busca la Availability del día de la semana correspondiente.
        - Si no hay ninguna, devuelve lista vacía.
        """
        def to_local_date(value: date | datetime) -> date:
            """
            Devuelve un objeto date en zona local:

            • Si value ya es date → lo devuelve.
            • Si value es datetime → lo convierte a zona local y devuelve .date().
            """
            if isinstance(value, date) and not isinstance(value, datetime):
                return value
            if isinstance(value, datetime):
                if timezone.is_naive(value):
                    value = timezone.make_aware(value, timezone.get_default_timezone())
                return timezone.localtime(value).date()
            raise TypeError("Se esperaba date o datetime")
    
    # ------------------------------------------------------------------
    # Lectura
    # --------------------- ---------------------------------------------
        
        print("target_day: %s" % target_day)
        # 0) Convertir a date
        target_day = to_local_date(target_day)
        print("target_day: %s" % target_day, "weekday=%s" % target_day.isoweekday())
        
        # 1) Availability puntual
        availability: Optional[Availability] = (
            Availability.objects
            .prefetch_related("availabilityrange_set")
            .filter(type=AvailabilityDTO.TYPE_PUNCTUAL, punctual_day=target_day)
            .order_by('-created_at')  # Obtener la más reciente
            .first()
        )

        if availability is None:
            weekday = target_day.isoweekday()  # 1=Lunes ... 7=Domingo
            availability = (
                Availability.objects
                .prefetch_related("availabilityrange_set")
                .filter(type=AvailabilityDTO.TYPE_WEEKDAY, weekday=weekday)
                .order_by('-created_at')  # Obtener la más reciente
                .first()
            )

        if availability is None:
            return []

        return list(availability.availabilityrange_set.all())

    # ------------------------------------------------------------------
    # Nuevos métodos para el sistema de versionado
    # ------------------------------------------------------------------

    @staticmethod
    def get_availability_history_for_day(target_day: date) -> List[Dict[str, Any]]:
        """Devuelve el historial completo de disponibilidades para un día específico.
        
        Retorna una lista de disponibilidades ordenadas por fecha de creación,
        con información sobre los rangos temporales que cubren.
        """
        def to_local_date(value: date | datetime) -> date:
            if isinstance(value, date) and not isinstance(value, datetime):
                return value
            if isinstance(value, datetime):
                if timezone.is_naive(value):
                    value = timezone.make_aware(value, timezone.get_default_timezone())
                return timezone.localtime(value).date()
            raise TypeError("Se esperaba date o datetime")
        
        target_day = to_local_date(target_day)
        
        # Obtener todas las disponibilidades para este día (puntuales y por weekday)
        weekday = target_day.isoweekday()
        
        # Disponibilidades puntuales para este día
        punctual_availabilities = (
            Availability.objects
            .prefetch_related("availabilityrange_set")
            .filter(type=AvailabilityDTO.TYPE_PUNCTUAL, punctual_day=target_day)
            .order_by('created_at')
        )
        
        # Disponibilidades por weekday
        weekday_availabilities = (
            Availability.objects
            .prefetch_related("availabilityrange_set")
            .filter(type=AvailabilityDTO.TYPE_WEEKDAY, weekday=weekday)
            .order_by('created_at')
        )
        
        # Combinar y ordenar por fecha de creación
        all_availabilities = list(punctual_availabilities) + list(weekday_availabilities)
        all_availabilities.sort(key=lambda x: x.created_at)
        
        # Construir el historial con rangos temporales
        history = []
        for i, av in enumerate(all_availabilities):
            ranges = list(av.availabilityrange_set.all())
            
            # Determinar el rango temporal
            if i == 0:
                # Primera disponibilidad: desde el pasado hasta la siguiente fecha
                if len(all_availabilities) > 1:
                    next_date = timezone.localtime(all_availabilities[1].created_at).date()
                    # Usar el día anterior para "hasta"
                    previous_date = next_date - timedelta(days=1)
                    temporal_range = f"Del pasado hasta {previous_date.strftime('%d-%m-%Y')}"
                else:
                    temporal_range = "Del pasado en adelante"
            elif i == len(all_availabilities) - 1:
                # Última disponibilidad: desde su fecha en adelante
                current_date = timezone.localtime(av.created_at).date()
                temporal_range = f"Del {current_date.strftime('%d-%m-%Y')} en adelante"
            else:
                # Disponibilidad intermedia: entre dos fechas
                next_date = timezone.localtime(all_availabilities[i + 1].created_at).date()
                # Usar el día anterior para "hasta"
                previous_date = next_date - timedelta(days=1)
                current_date = timezone.localtime(av.created_at).date()
                temporal_range = f"Del {current_date.strftime('%d-%m-%Y')} al {previous_date.strftime('%d-%m-%Y')}"
            
            history.append({
                'id': av.id,
                'type': av.type,
                'punctual_day': av.punctual_day,
                'weekday': av.weekday,
                'created_at': av.created_at,
                'temporal_range': temporal_range,
                'ranges': [
                    {
                        'initial_time': r.initial_time,
                        'end_time': r.end_time,
                        'massagists_availability': r.massagists_availability,
                    }
                    for r in ranges
                ]
            })
        
        return history

    @staticmethod
    def get_availability_by_id(availability_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una disponibilidad específica por ID con sus rangos."""
        try:
            av = Availability.objects.prefetch_related("availabilityrange_set").get(id=availability_id)
            ranges = list(av.availabilityrange_set.all())
            
            return {
                'id': av.id,
                'type': av.type,
                'punctual_day': av.punctual_day,
                'weekday': av.weekday,
                'created_at': av.created_at,
                'ranges': [
                    {
                        'initial_time': r.initial_time,
                        'end_time': r.end_time,
                        'massagists_availability': r.massagists_availability,
                    }
                    for r in ranges
                ]
            }
        except Availability.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def create_new_weekday_availability_version(
        weekday: int,
        ranges: List[AvailabilityRangeDTO],
        effective_date: Optional[date] = None
    ) -> Availability:
        """Crea una nueva versión de disponibilidad para un día de la semana.
        
        Args:
            weekday: El día de la semana (1=Lunes, 2=Martes, ..., 7=Domingo)
            ranges: Los rangos horarios de la nueva disponibilidad
            effective_date: Fecha efectiva (si no se proporciona, usa hoy)
        """
        if effective_date is None:
            effective_date = timezone.now().date()
        
        # Crear la nueva disponibilidad por weekday
        # Usar timezone.localtime() para mantener en zona horaria local
        local_datetime = timezone.localtime(
            timezone.make_aware(
                datetime.combine(effective_date, datetime.min.time())
            )
        )
        
        availability = Availability.objects.create(
            type=AvailabilityDTO.TYPE_WEEKDAY,
            weekday=weekday,
            punctual_day=None,
            created_at=local_datetime
        )
        
        # Crear los rangos
        AvailabilityManager._create_related_ranges(availability, ranges)
        
        return availability

    @staticmethod
    @transaction.atomic
    def create_new_availability_version(
        target_day: date,
        ranges: List[AvailabilityRangeDTO],
        effective_date: Optional[date] = None
    ) -> Availability:
        """Crea una nueva versión de disponibilidad para un día específico.
        
        Args:
            target_day: El día para el que se crea la disponibilidad
            ranges: Los rangos horarios de la nueva disponibilidad
            effective_date: Fecha efectiva (si no se proporciona, usa hoy)
        """
        if effective_date is None:
            effective_date = timezone.now().date()
        
        # Determinar si es puntual o weekday
        weekday = target_day.isoweekday()
        
        # Crear la nueva disponibilidad
        # Usar timezone.localtime() para mantener en zona horaria local
        local_datetime = timezone.localtime(
            timezone.make_aware(
                datetime.combine(effective_date, datetime.min.time())
            )
        )
        
        availability = Availability.objects.create(
            type=AvailabilityDTO.TYPE_PUNCTUAL,
            punctual_day=target_day,
            weekday=None,
            created_at=local_datetime
        )
        
        # Crear los rangos
        AvailabilityManager._create_related_ranges(availability, ranges)
        
        return availability

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
