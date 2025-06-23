"""Gestor de operaciones CRUD para GiftVoucher.

Esta implementación sigue el patrón de otros *managers* del proyecto. Se basa
en los DTOs definidos en ``reservations.dtos.gift_voucher`` para exponer los
datos y en el modelo ``GiftVoucher`` para la persistencia.
"""

from __future__ import annotations

import random
from typing import List, Optional

from django.db import transaction
from django.utils import timezone

from reservations.dtos.gift_voucher import GiftVoucherDTO
from reservations.models import GiftVoucher


class GiftVoucherManager:
    """Gestor CRUD para *cheques regalo* (GiftVoucher)."""

    # ------------------------------------------------------------------
    # Conversión -> DTO
    # ------------------------------------------------------------------

    @staticmethod
    def _to_dto(voucher: GiftVoucher) -> GiftVoucherDTO:
        """Convierte un modelo GiftVoucher en GiftVoucherDTO."""

        return GiftVoucherDTO(
            id=voucher.id,
            code=voucher.code,
            price=voucher.price,
            used=voucher.used,
            buyer_client_id=voucher.buyer_client_id,
            product_id=voucher.product_id,
            recipients_email=voucher.recipients_email,
            recipients_name=voucher.recipients_name,
            recipients_surname=voucher.recipients_surname,
            gift_name=voucher.gift_name,
            gift_description=voucher.gift_description,
            created_at=voucher.created_at,
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
            product_id=dto.product_id,
        )

        return GiftVoucherManager._to_dto(voucher)

    # ------------------------------------------------------------------
    @staticmethod
    def list_vouchers() -> List[GiftVoucherDTO]:
        """Devuelve todos los cheques regalo ordenados por fecha de creación."""

        vouchers = GiftVoucher.objects.all().order_by("-created_at")
        return [GiftVoucherManager._to_dto(v) for v in vouchers]

    # ------------------------------------------------------------------
    @staticmethod
    def get_voucher(voucher_id: int) -> Optional[GiftVoucherDTO]:
        """Devuelve el DTO de un cheque regalo o ``None`` si no existe."""

        voucher = GiftVoucher.objects.filter(id=voucher_id).first()
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
            "product_id": dto.product_id,
        }

        changed_fields = []
        for field, value in fields_map.items():
            if value is not None:
                setattr(voucher, field, value)
                changed_fields.append(field)

        if changed_fields:
            voucher.save(update_fields=changed_fields)

        return GiftVoucherManager._to_dto(voucher)

    # ------------------------------------------------------------------
    @staticmethod
    @transaction.atomic
    def delete_voucher(voucher_id: int) -> None:
        """Elimina un GiftVoucher."""

        GiftVoucher.objects.filter(id=voucher_id).delete()
