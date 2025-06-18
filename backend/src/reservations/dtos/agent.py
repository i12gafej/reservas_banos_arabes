from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AgentDTO:
    """DTO único para Agente (creación, actualización, retorno)."""

    id: Optional[int] = None
    name: Optional[str] = None
    platform: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    # Validaciones -----------------------------------------------------------
    def validate_for_create(self):
        if not self.name:
            raise ValueError("El nombre es obligatorio")

    def validate_for_update(self):
        if self.id is None:
            raise ValueError("Se requiere 'id' para actualizar un agente")
