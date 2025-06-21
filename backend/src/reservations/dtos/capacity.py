from dataclasses import dataclass

@dataclass
class CapacityDTO:
    """DTO simple para el modelo Capacity (aforo)."""

    value: int

    def validate(self) -> None:
        if self.value <= 0:
            raise ValueError("El aforo debe ser mayor que 0")
