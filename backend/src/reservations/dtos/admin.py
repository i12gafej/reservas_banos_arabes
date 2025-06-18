from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AdminDTO:
    """DTO único para Administrador (creación, actualización, retorno)."""

    id: Optional[int] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None  # solo al crear
    created_at: Optional[datetime] = None

    # Validaciones -----------------------------------------------------------
    def validate_for_create(self):
        if not self.name:
            raise ValueError("El nombre es obligatorio")
        if not self.email:
            raise ValueError("El email es obligatorio")
        if not self.password:
            raise ValueError("La contraseña es obligatoria")

    def validate_for_update(self):
        if self.id is None:
            raise ValueError("Se requiere 'id' para actualizar un administrador")
