from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional


# ---------------------------------------------------------------------------
# DTOs auxiliares
# ---------------------------------------------------------------------------

@dataclass
class GiftProductQuantityDTO:
    """Relación producto–cantidad dentro de un cheque regalo."""

    product_id: int
    quantity: int = 1

    def validate(self) -> None:
        if self.quantity <= 0:
            raise ValueError("La cantidad debe ser mayor que 0")


# ---------------------------------------------------------------------------
# DTOs principales
# ---------------------------------------------------------------------------

@dataclass
class GiftVoucherDTO:
    """DTO único para creación, actualización y retorno de Cheque Regalo."""

    # Identificador (None al crear)
    id: Optional[int] = None
    code: Optional[str] = None  # Rellenado al devolver

    price: Optional[Decimal] = None
    used: Optional[bool] = None

    buyer_client_id: Optional[int] = None

    recipients_email: Optional[str] = None
    recipients_name: Optional[str] = None
    recipients_surname: Optional[str] = None
    gift_name: Optional[str] = None
    gift_description: Optional[str] = None

    created_at: Optional[datetime] = None

    products: List[GiftProductQuantityDTO] = field(default_factory=list)

    # Validaciones -----------------------------------------------------------
    def validate_for_create(self):
        if self.price is None or self.price < 0:
            raise ValueError("El precio debe ser un número positivo")
        if self.buyer_client_id is None:
            raise ValueError("Debe indicar 'buyer_client_id'")
        if not self.products:
            raise ValueError("Debe incluir al menos un producto")
        for p in self.products:
            p.validate()

    def validate_for_update(self):
        if self.id is None:
            raise ValueError("Se requiere 'id' para actualizar el cheque regalo")
        if self.products:
            for p in self.products:
                p.validate()

