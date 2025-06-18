"""Gestor de operaciones CRUD para GiftVoucher y ProductsInGift.

Esta implementación sigue el patrón de otros *managers* del proyecto. Se basa
en los DTOs definidos en ``reservations.dtos.gift_voucher`` para exponer los
datos y en los modelos ``GiftVoucher`` y ``ProductsInGift`` para la
persistencia.
"""

from __future__ import annotations

import random
from typing import List, Optional

from django.db import transaction
from django.utils import timezone

from reservations.dtos.gift_voucher import (
    GiftVoucherDTO,
    GiftProductQuantityDTO,
)
from reservations.models import GiftVoucher, ProductsInGift


class GiftVoucherManager:
    """Gestor CRUD para *cheques regalo* (GiftVoucher)."""

    # ------------------------------------------------------------------
    # Conversión -> DTO
    # ------------------------------------------------------------------

    @staticmethod
    def _to_dto(voucher: GiftVoucher) -> GiftVoucherDTO:
        """Convierte un modelo GiftVoucher en GiftVoucherDTO."""

        products = [
            GiftProductQuantityDTO(product_id=p.product_id, quantity=p.quantity)
            for p in voucher.productsingift_set.all()
        ]

        return GiftVoucherDTO(
            id=voucher.id,
            code=voucher.code,
            price=voucher.price,
            used=voucher.used,
            buyer_client_id=voucher.buyer_client_id,
            recipients_email=voucher.recipients_email,
            recipients_name=voucher.recipients_name,
            recipients_surname=voucher.recipients_surname,
            gift_name=voucher.gift_name,
            gift_description=voucher.gift_description,
            created_at=voucher.created_at,
            products=products,
        )

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_unique_code() -> str:
        """Genera un código único con formato ddmmyyyy + 4 dígitos aleatorios."""

        today = timezone.now().strftime("%d%m%Y")
        while True:
            random_digits = "".join(str(random.randint(0, 9)) for _ in range(4))
            code = f"{today}{random_digits}"
            if not GiftVoucher.objects.filter(code=code).exists():
                return code

    @staticmethod
    def _create_products(voucher: GiftVoucher, products: List[GiftProductQuantityDTO]) -> None:
        """Crea registros ProductsInGift."""

        for p in products:
            p.validate()
            ProductsInGift.objects.create(
                gift=voucher,
                product_id=p.product_id,
                quantity=p.quantity,
            )

    # ------------------------------------------------------------------
    # CRUD público
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def create_voucher(dto: GiftVoucherDTO) -> GiftVoucherDTO:
        """Crea un GiftVoucher y devuelve su DTO."""

        dto.validate_for_create()

        voucher = GiftVoucher.objects.create(
            code=GiftVoucherManager._generate_unique_code(),
            price=dto.price,
            used=dto.used or False,
            recipients_email=dto.recipients_email or "",
            recipients_name=dto.recipients_name or "",
            recipients_surname=dto.recipients_surname or "",
            gift_name=dto.gift_name or "",
            gift_description=dto.gift_description or "",
            buyer_client_id=dto.buyer_client_id,
        )

        GiftVoucherManager._create_products(voucher, dto.products)

        return GiftVoucherManager._to_dto(voucher)

    # ------------------------------------------------------------------
    @staticmethod
    def list_vouchers() -> List[GiftVoucherDTO]:
        """Devuelve todos los cheques regalo ordenados por fecha de creación."""

        vouchers = (
            GiftVoucher.objects.prefetch_related("productsingift_set").order_by("-created_at")
        )
        return [GiftVoucherManager._to_dto(v) for v in vouchers]

    # ------------------------------------------------------------------
    @staticmethod
    def get_voucher(voucher_id: int) -> Optional[GiftVoucherDTO]:
        """Devuelve el DTO de un cheque regalo o ``None`` si no existe."""

        voucher = (
            GiftVoucher.objects.prefetch_related("productsingift_set").filter(id=voucher_id).first()
        )
        if voucher is None:
            return None
        return GiftVoucherManager._to_dto(voucher)

    # ------------------------------------------------------------------
    @staticmethod
    @transaction.atomic
    def update_voucher(dto: GiftVoucherDTO) -> GiftVoucherDTO:
        """Actualiza un GiftVoucher existente y devuelve su DTO actualizado."""

        dto.validate_for_update()

        voucher = GiftVoucher.objects.get(id=dto.id)

        fields_map = {
            "price": dto.price,
            "used": dto.used,
            "recipients_email": dto.recipients_email,
            "recipients_name": dto.recipients_name,
            "recipients_surname": dto.recipients_surname,
            "gift_name": dto.gift_name,
            "gift_description": dto.gift_description,
        }

        changed_fields = []
        for field, value in fields_map.items():
            if value is not None:
                setattr(voucher, field, value)
                changed_fields.append(field)

        if changed_fields:
            voucher.save(update_fields=changed_fields)

        # Actualizar productos si se proporcionan
        if dto.products:
            # Reemplazar relaciones
            ProductsInGift.objects.filter(gift=voucher).delete()
            GiftVoucherManager._create_products(voucher, dto.products)

        return GiftVoucherManager._to_dto(voucher)

    # ------------------------------------------------------------------
    @staticmethod
    @transaction.atomic
    def delete_voucher(voucher_id: int) -> None:
        """Elimina un GiftVoucher."""

        GiftVoucher.objects.filter(id=voucher_id).delete()
