from typing import List

from django.db import transaction

from reservations.dtos.client import ClientDTO
from reservations.models import Client


class ClientManager:
    """Gestor de operaciones CRUD para clientes."""

    # ------------------------------------------------------------------
    # Crear
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def create_client(dto: ClientDTO) -> ClientDTO:
        dto.validate_for_create()
        client = Client.objects.create(
            name=dto.name,
            surname=dto.surname or "",
            phone_number=dto.phone_number or "",
            email=dto.email or None,
        )
        return ClientManager._to_dto(client)

    # ------------------------------------------------------------------
    # Actualizar
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def update_client(dto: ClientDTO) -> ClientDTO:
        dto.validate_for_update()
        client = Client.objects.get(id=dto.id)

        # Lista blanca de campos permitidos a sobreescribir
        fields_map = {
            "name": dto.name,
            "surname": dto.surname,
            "phone_number": dto.phone_number,
            "email": dto.email,
        }
        changed_fields = []
        for field, value in fields_map.items():
            if value is not None:
                setattr(client, field, value)
                changed_fields.append(field)
        if changed_fields:
            client.save(update_fields=changed_fields)
        return ClientManager._to_dto(client)

    # ------------------------------------------------------------------
    # Listar
    # ------------------------------------------------------------------

    @staticmethod
    def list_clients() -> List[ClientDTO]:
        return [ClientManager._to_dto(c) for c in Client.objects.all().order_by("-created_at")]

    # ------------------------------------------------------------------
    # Eliminar
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def delete_client(client_id: int) -> None:
        Client.objects.filter(id=client_id).delete()

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    @staticmethod
    def _to_dto(client: Client) -> ClientDTO:
        return ClientDTO(
            id=client.id,
            name=client.name,
            surname=client.surname,
            phone_number=client.phone_number,
            email=client.email,
            created_at=client.created_at,
        )
