from typing import List

from django.db import transaction

from reservations.dtos.client import (
    ClientCreateDTO,
    ClientUpdateDTO,
    ClientDTO,
    ClientListDTO,
    ClientDeleteDTO,
)
from reservations.models import Client


class ClientManager:
    """Gestor de operaciones CRUD para clientes."""

    # ------------------------------------------------------------------
    # Crear
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def create_client(dto: ClientCreateDTO) -> ClientDTO:
        dto.validate()
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
    def update_client(dto: ClientUpdateDTO) -> ClientDTO:
        dto.validate()
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
    def list_clients() -> ClientListDTO:
        clients = Client.objects.all().order_by("-created_at")
        return ClientListDTO(clients=[ClientManager._to_dto(c) for c in clients])

    # ------------------------------------------------------------------
    # Eliminar
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def delete_client(dto: ClientDeleteDTO) -> None:
        Client.objects.filter(id=dto.id).delete()

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
