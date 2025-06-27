from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional, List


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
    status: Optional[str] = None
    payment_date: Optional[datetime] = None
    people: Optional[int] = None

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


@dataclass
class GiftVoucherWithDetailsDTO:
    """DTO extendido para mostrar detalles completos de un cheque regalo incluyendo cliente y producto."""
    # Campos básicos de GiftVoucherDTO
    id: Optional[int] = None
    code: Optional[str] = None
    price: Optional[Decimal] = None
    status: Optional[str] = None
    payment_date: Optional[datetime] = None
    people: Optional[int] = None
    buyer_client_id: Optional[int] = None
    product_id: Optional[int] = None
    recipients_email: Optional[str] = None
    recipients_name: Optional[str] = None
    recipients_surname: Optional[str] = None
    gift_name: Optional[str] = None
    gift_description: Optional[str] = None
    created_at: Optional[datetime] = None
    bought_date: Optional[datetime] = None  # Alias para created_at
    
    # Información del cliente comprador
    buyer_name: Optional[str] = None
    buyer_surname: Optional[str] = None
    buyer_phone: Optional[str] = None
    buyer_email: Optional[str] = None
    buyer_client_created_at: Optional[datetime] = None
    
    # Información del producto
    product_name: Optional[str] = None


# ---------------------------------------------------------------------------
# DTO para crear cheques regalo desde staff
# ---------------------------------------------------------------------------

@dataclass
class StaffGiftVoucherPayloadDTO:
    """DTO para crear cheques regalo desde el staff con masajes y datos completos."""
    
    # Datos del comprador
    buyer_name: str = ""
    buyer_surname: str = ""
    buyer_phone: str = ""
    buyer_email: str = ""
    
    # Datos del destinatario (opcionales)
    recipient_name: Optional[str] = None
    recipient_surname: Optional[str] = None
    recipient_email: Optional[str] = None
    
    # Datos del cheque regalo
    gift_name: str = ""
    gift_description: str = ""
    people: int = 1
    
    # Masajes (similar a reservas)
    baths: Optional[List] = None  # Lista de StaffBathRequestDTO
    price: Optional[Decimal] = None
    
    # Otros
    send_whatsapp_buyer: bool = False
    
    def validate(self):
        if not self.buyer_name:
            raise ValueError("El nombre del comprador es obligatorio")
        if not self.buyer_email:
            raise ValueError("El email del comprador es obligatorio")
        if not self.gift_name:
            raise ValueError("El nombre del cheque regalo es obligatorio")
        if self.people <= 0:
            raise ValueError("El número de personas debe ser mayor que 0")
        if not self.baths:
            raise ValueError("Debe indicar al menos un tipo de baño/masaje")

