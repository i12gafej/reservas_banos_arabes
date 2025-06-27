from dataclasses import dataclass, field
from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, List, Tuple


@dataclass
class BookLogDTO:
    """DTO para logs de reservas."""
    id: Optional[int] = None
    book_id: Optional[int] = None
    datetime: Optional[datetime] = None
    comment: str = ""

    def validate_for_create(self):
        if not self.book_id:
            raise ValueError("Se requiere 'book_id' para crear un log")
        if not self.comment:
            raise ValueError("Se requiere 'comment' para crear un log")


@dataclass
class BookDetailDTO:
    """DTO extendido para mostrar detalles completos de una reserva."""
    # Campos básicos de BookDTO
    id: Optional[int] = None
    internal_order_id: Optional[str] = None
    booking_date: Optional[date] = None
    hour: Optional[time] = None
    people: Optional[int] = 1
    comment: Optional[str] = None
    observation: Optional[str] = None
    amount_paid: Optional[Decimal] = Decimal("0")
    amount_pending: Optional[Decimal] = Decimal("0")
    payment_date: Optional[datetime] = None
    checked_in: Optional[bool] = None
    checked_out: Optional[bool] = None
    client_id: Optional[int] = None
    product_id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    # Información del cliente
    client_name: Optional[str] = None
    client_surname: Optional[str] = None
    client_phone: Optional[str] = None
    client_email: Optional[str] = None
    client_created_at: Optional[datetime] = None
    
    # Información del creador
    creator_type_name: Optional[str] = None
    creator_name: Optional[str] = None
    
    # Información del producto (masajes)
    product_baths: Optional[List] = None


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
    # Datos cliente - opción 1: usar cliente existente
    client_id: Optional[int] = None
    # Datos cliente - opción 2: crear cliente nuevo
    name: str = ""
    surname: str = ""
    phone_number: str = ""
    email: str = ""
    # Datos reserva
    date: str = ""
    hour: str = ""
    people: int = 1
    comment: Optional[str] = None
    force: bool = False  # Para saltarse validaciones de disponibilidad
    # Campos del creador (para cheques regalo)
    creator_type_id: Optional[int] = None
    creator_id: Optional[int] = None

    def validate(self):
        if not self.product_id and not self.baths:
            raise ValueError("Debe indicar product_id o baths para la reserva staff")
        
        # Validar que se proporcione client_id O datos del nuevo cliente
        if not self.client_id and not self.name:
            raise ValueError("Debe indicar client_id o los datos del cliente (name) para crear la reserva")


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
    observation: Optional[str] = None

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


@dataclass
class BookMassageUpdateDTO:
    """DTO para actualizar masajes de una reserva existente."""
    massage60Relax: int = 0
    massage60Piedra: int = 0
    massage60Exfol: int = 0
    massage30Relax: int = 0
    massage30Piedra: int = 0
    massage30Exfol: int = 0
    massage15Relax: int = 0
    people: int = 1  # Número de personas para calcular baños sin masaje

    def to_staff_bath_requests(self) -> List[StaffBathRequestDTO]:
        """Convierte los valores de masajes a una lista de StaffBathRequestDTO incluyendo baños sin masaje."""
        baths = []
        
        # Mapeo de campos a tipos de masaje
        massage_map = {
            'massage60Relax': ('relax', '60'),
            'massage60Piedra': ('rock', '60'), 
            'massage60Exfol': ('exfoliation', '60'),
            'massage30Relax': ('relax', '30'),
            'massage30Piedra': ('rock', '30'),
            'massage30Exfol': ('exfoliation', '30'),
            'massage15Relax': ('relax', '15'),
        }
        
        # Contar total de masajes
        total_massages = 0
        for field_name, (massage_type, duration) in massage_map.items():
            quantity = getattr(self, field_name, 0)
            if quantity > 0:
                baths.append(StaffBathRequestDTO(
                    massage_type=massage_type,
                    minutes=duration,
                    quantity=quantity
                ))
                total_massages += quantity
        
        # Agregar baños sin masaje para las personas restantes
        people_without_massage = self.people - total_massages
        if people_without_massage > 0:
            baths.append(StaffBathRequestDTO(
                massage_type='none',
                minutes='0',
                quantity=people_without_massage
            ))
        
        return baths
