from dataclasses import dataclass, field
from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, List


@dataclass
class StaffBathRequestDTO:
    """Descripción mínima de un lote de baños (tipo + minutos + cantidad)."""

    massage_type: str   # 'relax' | 'exfoliation' | 'rock' | 'none'
    minutes: str        # '15' | '30' | '60'
    quantity: int = 1

    def validate(self):
        # Permitir que llegue como string desde JSON
        try:
            self.quantity = int(self.quantity)
        except (TypeError, ValueError):
            raise ValueError("'quantity' debe ser un entero positivo")

        if self.quantity <= 0:
            raise ValueError("La cantidad debe ser mayor que 0")


@dataclass
class StaffBookingPayloadDTO:
    # Opción 1: producto existente
    product_id: Optional[int] = None
    # Opción 2: crear producto nuevo
    baths: Optional[List[StaffBathRequestDTO]] = None
    price: Optional[Decimal] = None
    # Datos cliente y reserva
    name: str = ""
    surname: str = ""
    phone: str = ""
    email: str = ""
    date: str = ""
    hour: str = ""
    people: int = 1
    comment: Optional[str] = None

    def validate(self):
        if not self.product_id and not self.baths:
            raise ValueError("Debe indicar product_id o baths para la reserva staff")


@dataclass
class BookDTO:
    """DTO único para creación/actualización/devolución de Book."""

    # Identificadores
    id: Optional[int] = None
    internal_order_id: Optional[str] = None  # Generado al crear

    # Datos básicos
    booking_date: Optional[date] = None  # Día de la reserva
    hour: Optional[time] = None
    people: Optional[int] = 1
    comment: Optional[str] = None

    amount_paid: Optional[Decimal] = Decimal("0")
    amount_pending: Optional[Decimal] = Decimal("0")

    payment_date: Optional[datetime] = None
    checked_in: Optional[bool] = None
    checked_out: Optional[bool] = None

    client_id: Optional[int] = None
    product_id: Optional[int] = None

    created_at: Optional[datetime] = None

    # Validaciones -----------------------------------------------------------
    def validate_for_create(self):
        if self.booking_date is None:
            raise ValueError("Debe indicar 'booking_date'")
        if self.client_id is None:
            raise ValueError("Debe indicar 'client_id'")
        if self.product_id is None:
            raise ValueError("Debe indicar 'product_id'")

    def validate_for_update(self):
        if self.id is None:
            raise ValueError("Se requiere 'id' para actualizar la reserva")
        if self.product_id is None:
            raise ValueError("Debe indicar 'product_id'")
