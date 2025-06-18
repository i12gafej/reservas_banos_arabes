from dataclasses import dataclass, field
from datetime import time, date
from typing import List, Optional


@dataclass
class AvailabilityRangeDTO:
    """Representa un tramo horario con su aforo y masajistas disponibles."""

    initial_time: time  # Hora de inicio (incluida)
    end_time: time      # Hora final (excluida normalmente)
    capacity: int
    massagists_availability: int

    def validate(self) -> None:
        if self.initial_time >= self.end_time:
            raise ValueError("La hora inicial debe ser anterior a la hora final")
        if self.capacity <= 0:
            raise ValueError("La capacidad debe ser mayor que 0")
        if self.massagists_availability < 0:
            raise ValueError("La disponibilidad de masajistas no puede ser negativa")


@dataclass
class AvailabilityDTO:
    """DTO para crear/editar una Availability con sus rangos horarios."""

    TYPE_WEEKDAY = "weekday"
    TYPE_PUNCTUAL = "punctual"

    type: str  # "weekday" o "punctual"
    punctual_day: Optional[date] = None
    weekday: Optional[int] = None  # 1=Lunes, 7=Domingo
    ranges: List[AvailabilityRangeDTO] = field(default_factory=list)

    def validate(self) -> None:
        if self.type not in {self.TYPE_WEEKDAY, self.TYPE_PUNCTUAL}:
            raise ValueError("Tipo de disponibilidad inválido")

        if self.type == self.TYPE_WEEKDAY and (self.weekday is None or not 1 <= self.weekday <= 7):
            raise ValueError("Para tipo 'weekday' se debe indicar 'weekday' entre 1 y 7")

        if self.type == self.TYPE_PUNCTUAL and self.punctual_day is None:
            raise ValueError("Para tipo 'punctual' se debe indicar 'punctual_day'")

        if not self.ranges:
            raise ValueError("Debe proporcionar al menos un rango de disponibilidad")

        for r in self.ranges:
            r.validate()
