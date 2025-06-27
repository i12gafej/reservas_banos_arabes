from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


# ---------------------------------------------------------------------------
# DTOs de Cliente
# ---------------------------------------------------------------------------

@dataclass
class ClientDTO:
    """DTO único para cliente: puede usarse para crear, actualizar o devolver datos."""

    # Identificador (None cuando aún no se ha creado)
    id: Optional[int] = None

    # Datos editables
    name: Optional[str] = None
    surname: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None

    # Sólo lectura (se rellena al devolver datos)
    created_at: Optional[datetime] = None
    
    # Información de coincidencias para búsquedas (opcional)
    match_info: Optional[Dict[str, bool]] = None

    # Métodos de validación contextuales --------------------------------------------------
    def validate_for_create(self):
        if not self.name:
            raise ValueError("El nombre es obligatorio para crear un cliente")

    def validate_for_update(self):
        if not self.id:
            raise ValueError("Se requiere 'id' para actualizar un cliente")