from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional


@dataclass
class ProductInBookDTO:
    """Relación producto-cantidad y disponibilidad dentro de una reserva."""

    product_id: int
    quantity: int = 1
    availability_id: Optional[int] = None  # Rango horario concreto usado

    def validate(self):
        if self.quantity <= 0:
            raise ValueError("La cantidad debe ser mayor que 0")


@dataclass
class BookDTO:
    """DTO único para creación/actualización/devolución de Book."""

    # Identificadores
    id: Optional[int] = None
    internal_order_id: Optional[str] = None  # Generado al crear

    # Datos básicos
    booking_date: Optional[datetime] = None  # Día de la reserva
    people: Optional[int] = 1
    comment: Optional[str] = None

    amount_paid: Optional[Decimal] = Decimal("0")
    amount_pending: Optional[Decimal] = Decimal("0")

    payment_date: Optional[datetime] = None
    checked_in: Optional[bool] = None
    checked_out: Optional[bool] = None

    client_id: Optional[int] = None

    # Productos incluidos
    products: List[ProductInBookDTO] = field(default_factory=list)

    created_at: Optional[datetime] = None

    # Validaciones -----------------------------------------------------------
    def validate_for_create(self):
        if self.booking_date is None:
            raise ValueError("Debe indicar 'booking_date'")
        if self.client_id is None:
            raise ValueError("Debe indicar 'client_id'")
        if not self.products:
            raise ValueError("Debe incluir al menos un producto en la reserva")
        for p in self.products:
            p.validate()

    def validate_for_update(self):
        if self.id is None:
            raise ValueError("Se requiere 'id' para actualizar la reserva")
        if self.products:
            for p in self.products:
                p.validate()
