from dataclasses import dataclass
from datetime import date, time
from typing import List


@dataclass
class ConstraintRangeDTO:
    """DTO para rangos de restricción."""
    initial_time: time
    end_time: time
    
    def __str__(self):
        return f"{self.initial_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"


@dataclass
class ConstraintDTO:
    """DTO para restricciones de reservas."""
    day: date
    ranges: List[ConstraintRangeDTO]
    id: int = None
    
    def __str__(self):
        return f"Restricción {self.day.strftime('%d/%m/%Y')} ({len(self.ranges)} rangos)"
