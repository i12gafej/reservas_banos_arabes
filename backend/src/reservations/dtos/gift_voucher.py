from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional


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
    product_id: Optional[int] = None

    recipients_email: Optional[str] = None
    recipients_name: Optional[str] = None
    recipients_surname: Optional[str] = None
    gift_name: Optional[str] = None
    gift_description: Optional[str] = None

    created_at: Optional[datetime] = None

    # Validaciones -----------------------------------------------------------
    def validate_for_create(self):
        if self.price is None or self.price < 0:
            raise ValueError("El precio debe ser un número positivo")
        if self.buyer_client_id is None:
            raise ValueError("Debe indicar 'buyer_client_id'")
        if self.product_id is None:
            raise ValueError("Debe indicar 'product_id'")

    def validate_for_update(self):
        if self.id is None:
            raise ValueError("Se requiere 'id' para actualizar el cheque regalo")

