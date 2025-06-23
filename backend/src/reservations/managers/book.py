"""Gestor CRUD simplificado para reservas (Book).

Esta implementación cubre las necesidades mínimas para que los ViewSets y los
Serializers funcionen sin lanzar ImportError. Las reglas de negocio completas
deberán desarrollarse más adelante (por ejemplo, gestión de ProductsInBook,
control de disponibilidad, etc.)."""

from typing import List

import random
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from reservations.dtos.book import BookDTO, StaffBathRequestDTO
from reservations.models import Book, Product, BathType, ProductBaths, Client


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
        """Convierte un modelo Book en BookDTO."""
        return BookDTO(
            id=book.id,
            internal_order_id=book.internal_order_id,
            booking_date=book.book_date,
            hour=book.hour,
            people=book.people,
            comment=book.comment,
            amount_paid=book.amount_paid,
            amount_pending=book.amount_pending,
            payment_date=book.payment_date,
            checked_in=book.checked_in,
            checked_out=book.checked_out,
            client_id=book.client_id,
            created_at=book.created_at,
            product_id=book.product_id,
        )

    # ------------------------------------------------------------------
    # Listado
    # ------------------------------------------------------------------

    @staticmethod
    def list_bookings() -> List[BookDTO]:
        """Devuelve todas las reservas ordenadas por creación."""
        return [BookManager._to_dto(b) for b in Book.objects.all().order_by("-created_at")]

    @staticmethod
    def list_bookings_by_date(booking_date: str) -> List[BookDTO]:
        """Devuelve todas las reservas de una fecha específica ordenadas por hora."""
        return [BookManager._to_dto(b) for b in Book.objects.filter(book_date=booking_date).order_by("hour")]

    # ------------------------------------------------------------------
    # Creación
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def create_booking(dto: BookDTO) -> BookDTO:
        """Crea un Book."""
        book = Book.objects.create(
            internal_order_id=BookManager._generate_internal_order_id(),
            book_date=dto.booking_date,
            hour=dto.hour,
            people=dto.people or 1,
            comment=dto.comment or "",
            amount_paid=dto.amount_paid or 0,
            amount_pending=dto.amount_pending or 0,
            payment_date=dto.payment_date,
            checked_in=dto.checked_in or False,
            checked_out=dto.checked_out or False,
            client_id=dto.client_id,
            product_id=dto.product_id,
        )
        return BookManager._to_dto(book)

    # ------------------------------------------------------------------
    # Actualización
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def update_booking(dto: BookDTO) -> BookDTO:
        """Actualiza campos básicos de un Book existente."""
        book = Book.objects.get(id=dto.id)
        fields_map = {
            "book_date": dto.booking_date,
            "hour": dto.hour,
            "people": dto.people,
            "comment": dto.comment,
            "amount_paid": dto.amount_paid,
            "amount_pending": dto.amount_pending,
            "payment_date": dto.payment_date,
            "checked_in": dto.checked_in,
            "checked_out": dto.checked_out,
            "product_id": dto.product_id,
        }
        changed_fields = []
        for field, value in fields_map.items():
            if value is not None:
                setattr(book, field, value)
                changed_fields.append(field)
        if changed_fields:
            book.save(update_fields=changed_fields)
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

    # ------------------------------------------------------------------
    # Creación desde STAFF
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def create_booking_from_staff(
        *,
        product_id: int = None,
        baths: List[StaffBathRequestDTO] = None,
        price: Decimal = None,
        name: str,
        surname: str,
        phone: str,
        email: str,
        date: str,
        hour: str,
        people: int,
        comment: str = "",
    ) -> BookDTO:
        client = Client.objects.create(
            name=name,
            surname=surname,
            phone_number=phone,
            email=email,
        )
        # Si se pasa product_id, usarlo directamente
        if product_id:
            book = Book.objects.create(
                internal_order_id=BookManager._generate_internal_order_id(),
                book_date=date,
                hour=hour,
                people=people,
                comment=comment,
                amount_paid=Decimal("0"),
                amount_pending=price or Decimal("0"),
                client=client,
                product_id=product_id,
            )
            return BookManager._to_dto(book)
        # Si no, crear producto nuevo o buscar uno idéntico
        if not baths:
            raise ValueError("Debe indicar baths si no se pasa product_id")
        # Buscar producto idéntico (mismos baths y precio)
        from reservations.models import ProductBaths
        bath_types = []
        for br in baths:
            br.validate()
            bath_types.append((br.massage_type, br.minutes, br.quantity))
        # Buscar productos con mismo precio
        candidates = Product.objects.filter(price=price or 0)
        for prod in candidates:
            prod_baths = list(prod.baths.values_list('bath_type__massage_type', 'bath_type__massage_duration', 'quantity'))
            if sorted(prod_baths) == sorted(bath_types):
                # Coincide exactamente
                book = Book.objects.create(
                    internal_order_id=BookManager._generate_internal_order_id(),
                    book_date=date,
                    hour=hour,
                    people=people,
                    comment=comment,
                    amount_paid=Decimal("0"),
                    amount_pending=price or Decimal("0"),
                    client=client,
                    product=prod,
                )
                return BookManager._to_dto(book)
        # Si no existe, crear producto y sus ProductBaths
        product = Product.objects.create(
            name=f"Reserva staff {date} {hour}",
            price=price or 0,
            uses_capacity=True,
            uses_massagist=True,
            visible=False,
        )
        for br in baths:
            bath_type, _ = BathType.objects.get_or_create(
                massage_type=br.massage_type,
                massage_duration=br.minutes,
                defaults={
                    "name": f"{br.massage_type.title()} {br.minutes}'",
                    "baths_duration": "02:00:00",
                    "description": "Autocreado (staff)",
                    "price": Decimal("0.00"),
                },
            )
            ProductBaths.objects.create(
                product=product,
                bath_type=bath_type,
                quantity=br.quantity,
            )
        book = Book.objects.create(
            internal_order_id=BookManager._generate_internal_order_id(),
            book_date=date,
            hour=hour,
            people=people,
            comment=comment,
            amount_paid=Decimal("0"),
            amount_pending=price or Decimal("0"),
            client=client,
            product=product,
        )
        return BookManager._to_dto(book)
