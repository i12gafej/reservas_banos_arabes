from typing import List

from django.db import transaction

from reservations.dtos.admin import AdminDTO
from reservations.models import Admin


class AdminManager:
    """Gestor CRUD para administradores."""

    # ------------------------------------------------------------------
    # Crear
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def create_admin(dto: AdminDTO) -> AdminDTO:
        dto.validate_for_create()
        admin = Admin.objects.create(
            name=dto.name,
            surname=dto.surname or "",
            phone_number=dto.phone_number or "",
            email=dto.email,
            password=dto.password,  # En un entorno real se debe hashear
        )
        return AdminManager._to_dto(admin)

    # ------------------------------------------------------------------
    # Actualizar
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def update_admin(dto: AdminDTO) -> AdminDTO:
        dto.validate_for_update()
        admin = Admin.objects.get(id=dto.id)

        fields_map = {
            "name": dto.name,
            "surname": dto.surname,
            "phone_number": dto.phone_number,
            "email": dto.email,
            "password": dto.password,
        }
        changed_fields = []
        for field, value in fields_map.items():
            if value is not None:
                setattr(admin, field, value)
                changed_fields.append(field)
        if changed_fields:
            admin.save(update_fields=changed_fields)
        return AdminManager._to_dto(admin)

    # ------------------------------------------------------------------
    # Listar
    # ------------------------------------------------------------------

    @staticmethod
    def list_admins() -> List[AdminDTO]:
        return [AdminManager._to_dto(a) for a in Admin.objects.all().order_by("name", "surname")]

    # ------------------------------------------------------------------
    # Eliminar
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def delete_admin(admin_id: int) -> None:
        Admin.objects.filter(id=admin_id).delete()

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    @staticmethod
    def _to_dto(admin: Admin) -> AdminDTO:
        return AdminDTO(
            id=admin.id,
            name=admin.name,
            surname=admin.surname,
            phone_number=admin.phone_number,
            email=admin.email,
            created_at=admin.created_at,
        )
