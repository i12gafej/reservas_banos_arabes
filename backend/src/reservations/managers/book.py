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

from reservations.dtos.book import BookDTO, ProductInBookDTO, StaffBathRequestDTO
from reservations.models import Book, ProductsInBook, Product, BathType, ProductBaths, Client


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
        """Convierte un modelo Book en BookDTO (incluye productos)."""

        # Obtener los productos asociados a la reserva
        product_dtos: List[ProductInBookDTO] = []
        for pib in ProductsInBook.objects.filter(book_id=book.id):
            product_dtos.append(
                ProductInBookDTO(
                    product_id=pib.product_id,
                    quantity=pib.quantity,
                )
            )

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
            products=product_dtos,
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
        """Crea un Book junto con sus ProductsInBook asociados."""

        # Validación mínima (ya validada en DTO)
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
        )

        # TODO: Crear ProductsInBook según dto.products
        for product_dto in dto.products:
            ProductsInBook.objects.create(
                book=book,
                product_id=product_dto.product_id,
                quantity=product_dto.quantity,
            )

            # ------------------------------------------------------------------
            # Asegurar BathType y ProductBaths
            # ------------------------------------------------------------------

            try:
                prod = Product.objects.get(id=product_dto.product_id)
            except Product.DoesNotExist:
                continue  # el producto no existe; la validación superior lanzará error

            # Si el producto ya tiene un baño asociado, no hacemos nada
            if prod.baths.exists():
                continue

            # Crear (o reutilizar) un BathType genérico "Default" sin masaje
            bath_name = f"Default bath for {prod.name}"
            bath_type, _ = BathType.objects.get_or_create(
                name=bath_name,
                defaults={
                    "massage_type": "none",
                    "massage_duration": "0",
                    "baths_duration": "02:00:00",
                    "description": "Generado automáticamente al crear reserva",
                },
            )

            # Crear relación ProductBaths (cantidad 1 por defecto)
            ProductBaths.objects.get_or_create(
                product=prod,
                bath_type=bath_type,
                defaults={"quantity": 1},
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

        # Campos permitidos a actualizar
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

    # ------------------------------------------------------------------
    # Creación desde STAFF
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def create_booking_from_staff(
        *,
        name: str,
        surname: str,
        phone: str,
        email: str,
        date_str: str,
        hour_str: str,
        people: int,
        baths: List[StaffBathRequestDTO],
        comment: str = "",
    ) -> BookDTO:

        # 1) Cliente nuevo
        client = Client.objects.create(
            name=name,
            surname=surname,
            phone_number=phone,
            email=email,
        )

        prods: List[Product] = []
        total = Decimal("0")

        for br in baths:
            br.validate()

            bath_type, _ = BathType.objects.get_or_create(
                massage_type=br.massage_type,
                massage_duration=br.minutes,
                defaults={
                    "name": f"{dict(BathType.MASSAGE_TYPE_CHOICES).get(br.massage_type, br.massage_type.title())} {br.minutes}'",
                    "baths_duration": "02:00:00",
                    "description": "Autocreado (staff)",
                    "price": Decimal("0.00"),
                },
            )

            prod_name = f"{br.quantity} x {bath_type.name}"
            product, _ = Product.objects.get_or_create(
                name=prod_name,
                visible=False,
                defaults={
                    "price": bath_type.price * br.quantity,
                    "observation": "",
                    "description": "",
                    "uses_capacity": True,
                    "uses_massagist": bath_type.massage_type != "none",
                },
            )

            ProductBaths.objects.update_or_create(
                product=product,
                bath_type=bath_type,
                defaults={"quantity": br.quantity},
            )

            prods.append(product)
            total += product.price

        # 3) Reserva
        book = Book.objects.create(
            internal_order_id=BookManager._generate_internal_order_id(),
            book_date=date_str,
            hour=hour_str,
            people=people,
            comment=comment,
            amount_paid=Decimal("0"),
            amount_pending=total,
            client=client,
        )

        for p in prods:
            ProductsInBook.objects.create(book=book, product=p, quantity=1)

        return BookManager._to_dto(book)
