from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional


# ---------------------------------------------------------------------------
# DTOs de entidades básicas (ya existen como modelos en la BD)
# ---------------------------------------------------------------------------


@dataclass
class BathTypeDTO:
    """Datos que identifican/definen un BathType existente o a crear."""

    name: str
    massage_type: str
    massage_duration: str
    baths_duration: str  # formato 'HH:MM:SS'
    description: Optional[str] = None
    price: Optional[Decimal] = None
    id: Optional[int] = None  # Opcional: si viene, se usa para lookup directo


@dataclass
class HostingTypeDTO:
    """Datos que identifican/definen un HostingType existente o a crear."""

    name: str
    capacity: int
    description: Optional[str] = None
    id: Optional[int] = None


@dataclass
class BathQuantityDTO:
    """Relación BathType + cantidad dentro del producto."""

    bath_type: BathTypeDTO
    quantity: int = 1


@dataclass
class HostingQuantityDTO:
    """Relación HostingType + cantidad dentro del producto."""

    hosting_type: HostingTypeDTO
    quantity: int = 1


@dataclass
class ProductCreateDTO:
    """DTO principal para la creación de un Producto con sus componentes asociados."""

    # Atributos básicos del producto
    name: str
    price: Decimal
    observation: Optional[str] = None
    description: Optional[str] = None
    uses_capacity: bool = True
    uses_massagist: bool = False
    visible: bool = True

    # Componentes: listas de tipos de baño y alojamiento con cantidades
    baths: List[BathQuantityDTO] = field(default_factory=list)
    hostings: List[HostingQuantityDTO] = field(default_factory=list)

    

    def validate(self) -> None:
        """Lanza ValueError si los datos no son coherentes."""
        if not self.name:
            raise ValueError("El nombre del producto es obligatorio")
        if self.price < 0:
            raise ValueError("El precio no puede ser negativo")
        for b in self.baths:
            if b.quantity <= 0:
                raise ValueError("La cantidad de baños debe ser mayor que 0")
        for h in self.hostings:
            if h.quantity < 0:
                raise ValueError("La cantidad de alojamientos debe ser mayoro igual que 0")
