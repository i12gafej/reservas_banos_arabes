"""Gestor CRUD simplificado para reservas (Book).

Esta implementación cubre las necesidades mínimas para que los ViewSets y los
Serializers funcionen sin lanzar ImportError. Las reglas de negocio completas
deberán desarrollarse más adelante (por ejemplo, gestión de ProductsInBook,
control de disponibilidad, etc.)."""

from typing import List, Optional

import random

from django.db import transaction
from django.utils import timezone

from reservations.dtos.book import BookDTO
from reservations.models import Book


class BookManager:
    """Gestor de operaciones CRUD para objetos Book.

    NOTA: Implementación mínima. Muchos detalles (productos, validaciones de
    disponibilidad, cálculos de importes, etc.) quedan pendientes.
    """

    # ------------------------------------------------------------------
    # Conversión helper
    # ------------------------------------------------------------------

    @staticmethod
    def _to_dto(book: Book) -> BookDTO:
        """Convierte un modelo Book en BookDTO (sin productos)."""

        return BookDTO(
            id=book.id,
            internal_order_id=book.internal_order_id,
            booking_date=book.book_date,
            booking_time=book.hour,
            people=book.people,
            comment=book.comment,
            amount_paid=book.amount_paid,
            amount_pending=book.amount_pending,
            payment_date=book.payment_date,
            checked_in=book.checked_in,
            checked_out=book.checked_out,
            client_id=book.client_id,
            created_at=book.created_at,
            products=[],  # TODO: mapear ProductsInBook
        )

    # ------------------------------------------------------------------
    # Listado
    # ------------------------------------------------------------------

    @staticmethod
    def list_bookings() -> List[BookDTO]:
        """Devuelve todas las reservas ordenadas por creación."""

        return [BookManager._to_dto(b) for b in Book.objects.all().order_by("-created_at")]

    # ------------------------------------------------------------------
    # Creación
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def create_booking(dto: BookDTO) -> BookDTO:
        """Crea un Book. Solo cubre campos básicos y omite productos."""

        # Validación mínima (ya validada en DTO)
        book = Book.objects.create(
            internal_order_id=BookManager._generate_internal_order_id(),
            book_date=dto.booking_date,
            hour=dto.booking_time,
            people=dto.people or 1,
            comment=dto.comment or "",
            amount_paid=dto.amount_paid or 0,
            amount_pending=dto.amount_pending or 0,
            payment_date=dto.payment_date,
            checked_in=dto.checked_in or False,
            checked_out=dto.checked_out or False,
            client_id=dto.client_id,
        )

        # TODO: Crear ProductsInBook según dto.products

        return BookManager._to_dto(book)

    # ------------------------------------------------------------------
    # Actualización
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def update_booking(dto: BookDTO) -> BookDTO:
        """Actualiza campos básicos de un Book existente."""

        book = Book.objects.get(id=dto.id)

        # Campos permitidos a actualizar
        fields_map = {
            "book_date": dto.booking_date,
            "hour": dto.booking_time,
            "people": dto.people,
            "comment": dto.comment,
            "amount_paid": dto.amount_paid,
            "amount_pending": dto.amount_pending,
            "payment_date": dto.payment_date,
            "checked_in": dto.checked_in,
            "checked_out": dto.checked_out,
        }

        changed_fields = []
        for field, value in fields_map.items():
            if value is not None:
                setattr(book, field, value)
                changed_fields.append(field)

        if changed_fields:
            book.save(update_fields=changed_fields)

        # TODO: Gestionar cambios en productos (dto.products).

        return BookManager._to_dto(book)

    # ------------------------------------------------------------------
    # Eliminación
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def delete_booking(book_id: int) -> None:
        """Elimina la reserva especificada."""

        Book.objects.filter(id=book_id).delete()

    # ------------------------------------------------------------------
    # Generación de identificador interno
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_internal_order_id() -> str:
        """Genera un ID único con formato ddmmyyyy + 4 dígitos aleatorios."""

        today = timezone.now().strftime("%d%m%Y")
        new_id = ""
        while True:
            random_digits = "".join(str(random.randint(0, 9)) for _ in range(4))
            new_id = f"{today}{random_digits}"
            if not Book.objects.filter(internal_order_id=new_id).exists():
                break
        return new_id
