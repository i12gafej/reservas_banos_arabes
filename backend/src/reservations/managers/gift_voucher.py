"""Gestor de operaciones CRUD para GiftVoucher.

Esta implementación sigue el patrón de otros *managers* del proyecto. Se basa
en los DTOs definidos en ``reservations.dtos.gift_voucher`` para exponer los
datos y en el modelo ``GiftVoucher`` para la persistencia.
"""

from __future__ import annotations

import random
from typing import List, Optional
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from reservations.dtos.gift_voucher import GiftVoucherDTO, GiftVoucherWithDetailsDTO, StaffGiftVoucherPayloadDTO
from reservations.dtos.book import StaffBathRequestDTO
from reservations.models import GiftVoucher, Client, Product, BathType, ProductBaths


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
            
            status=voucher.status if hasattr(voucher, 'status') else None,
            payment_date=voucher.payment_date if hasattr(voucher, 'payment_date') else None,
            people=voucher.people if hasattr(voucher, 'people') else None,
            buyer_client_id=voucher.buyer_client_id,
            product_id=voucher.product_id,
            recipients_email=voucher.recipients_email,
            recipients_name=voucher.recipients_name,
            recipients_surname=voucher.recipients_surname,
            gift_name=voucher.gift_name,
            gift_description=voucher.gift_description,
            created_at=voucher.created_at,
        )

    @staticmethod
    def _to_details_dto(voucher: GiftVoucher) -> GiftVoucherWithDetailsDTO:
        """Convierte un modelo GiftVoucher en GiftVoucherWithDetailsDTO con información relacionada."""
        
        return GiftVoucherWithDetailsDTO(
            id=voucher.id,
            code=voucher.code,
            price=voucher.price,
            
            status=voucher.status if hasattr(voucher, 'status') else None,
            payment_date=voucher.payment_date if hasattr(voucher, 'payment_date') else None,
            people=voucher.people if hasattr(voucher, 'people') else None,
            buyer_client_id=voucher.buyer_client_id,
            product_id=voucher.product_id,
            recipients_email=voucher.recipients_email,
            recipients_name=voucher.recipients_name,
            recipients_surname=voucher.recipients_surname,
            gift_name=voucher.gift_name,
            gift_description=voucher.gift_description,
            created_at=voucher.created_at,
            bought_date=voucher.bought_date if hasattr(voucher, 'bought_date') else voucher.created_at,
            
            # Información del cliente comprador
            buyer_name=voucher.buyer_client.name if voucher.buyer_client else None,
            buyer_surname=voucher.buyer_client.surname if voucher.buyer_client else None,
            buyer_phone=voucher.buyer_client.phone_number if voucher.buyer_client else None,
            buyer_email=voucher.buyer_client.email if voucher.buyer_client else None,
            buyer_client_created_at=voucher.buyer_client.created_at if voucher.buyer_client else None,
            
            # Información del producto
            product_name=voucher.product.name if voucher.product else None,
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

        voucher_data = {
            'code': GiftVoucherManager._generate_unique_code(),
            'price': dto.price,
            'recipients_email': dto.recipients_email or "",
            'recipients_name': dto.recipients_name or "",
            'recipients_surname': dto.recipients_surname or "",
            'gift_name': dto.gift_name or "",
            'gift_description': dto.gift_description or "",
            'buyer_client_id': dto.buyer_client_id,
            'product_id': dto.product_id,
        }

        # Agregar campos nuevos si existen en el modelo
        if dto.status is not None:
            voucher_data['status'] = dto.status
        if dto.payment_date is not None:
            voucher_data['payment_date'] = dto.payment_date
        if dto.people is not None:
            voucher_data['people'] = dto.people

        voucher = GiftVoucher.objects.create(**voucher_data)

        return GiftVoucherManager._to_dto(voucher)

    # ------------------------------------------------------------------
    @staticmethod
    def list_vouchers() -> List[GiftVoucherDTO]:
        """Devuelve todos los cheques regalo ordenados por fecha de creación."""

        vouchers = GiftVoucher.objects.all().order_by("-created_at")
        return [GiftVoucherManager._to_dto(v) for v in vouchers]

    @staticmethod
    def list_vouchers_with_details() -> List[GiftVoucherWithDetailsDTO]:
        """Devuelve todos los cheques regalo con detalles completos ordenados por fecha de creación."""

        vouchers = GiftVoucher.objects.select_related('buyer_client', 'product').all().order_by("-created_at")
        return [GiftVoucherManager._to_details_dto(v) for v in vouchers]

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
            "recipients_email": dto.recipients_email,
            "recipients_name": dto.recipients_name,
            "recipients_surname": dto.recipients_surname,
            "gift_name": dto.gift_name,
            "gift_description": dto.gift_description,
            "product_id": dto.product_id,
        }

        # Agregar campos nuevos si existen
        
        if hasattr(voucher, 'status') and dto.status is not None:
            fields_map["status"] = dto.status
        if hasattr(voucher, 'payment_date') and dto.payment_date is not None:
            fields_map["payment_date"] = dto.payment_date
        if hasattr(voucher, 'people') and dto.people is not None:
            fields_map["people"] = dto.people

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
    # ------------------------------------------------------------------
    # Creación desde STAFF (similar a BookManager.create_booking_from_staff)
    # ------------------------------------------------------------------

    @staticmethod
    def ensure_bath_types_exist():
        """Asegura que existen todos los BathTypes necesarios en la base de datos."""
        # Definir todos los tipos de baño necesarios con sus precios por defecto
        required_bath_types = [
            # Baños sin masaje
            {
                'massage_type': 'none',
                'massage_duration': '0',
                'name': 'Baño sin masaje',
                'price': Decimal('20.00')
            },
            # Masajes de 60 minutos
            {
                'massage_type': 'relax',
                'massage_duration': '60',
                'name': 'Masaje Relajante 60min',
                'price': Decimal('30.00')
            },
            {
                'massage_type': 'rock',
                'massage_duration': '60',
                'name': 'Masaje Piedras 60min',
                'price': Decimal('35.00')
            },
            {
                'massage_type': 'exfoliation',
                'massage_duration': '60',
                'name': 'Masaje Exfoliante 60min',
                'price': Decimal('35.00')
            },
            # Masajes de 30 minutos
            {
                'massage_type': 'relax',
                'massage_duration': '30',
                'name': 'Masaje Relajante 30min',
                'price': Decimal('20.00')
            },
            {
                'massage_type': 'rock',
                'massage_duration': '30',
                'name': 'Masaje Piedras 30min',
                'price': Decimal('25.00')
            },
            {
                'massage_type': 'exfoliation',
                'massage_duration': '30',
                'name': 'Masaje Exfoliante 30min',
                'price': Decimal('25.00')
            },
            # Masajes de 15 minutos
            {
                'massage_type': 'relax',
                'massage_duration': '15',
                'name': 'Masaje Relajante 15min',
                'price': Decimal('15.00')
            },
        ]
        
        for bath_data in required_bath_types:
            BathType.objects.get_or_create(
                massage_type=bath_data['massage_type'],
                massage_duration=bath_data['massage_duration'],
                defaults={
                    'name': bath_data['name'],
                    'baths_duration': '02:00:00',
                    'description': 'Autocreado por sistema',
                    'price': bath_data['price'],
                }
            )

    @staticmethod
    @transaction.atomic
    def create_gift_voucher_from_staff(payload: StaffGiftVoucherPayloadDTO) -> GiftVoucherDTO:
        """Crea un cheque regalo desde el staff con masajes y cliente comprador."""
        
        payload.validate()
        
        # Validar que la cantidad de masajes no sea mayor a las personas
        if payload.baths and payload.people:
            total_baths = sum(bath.quantity for bath in payload.baths if bath.massage_type != 'none')
            if total_baths > payload.people:
                raise ValueError(f"Hay más masajes ({total_baths}) que personas ({payload.people}). Reduce la cantidad de masajes o aumenta el número de personas.")
        
        # Asegurar que existen todos los BathTypes necesarios
        GiftVoucherManager.ensure_bath_types_exist()
        
        # 1. Crear o encontrar cliente comprador
        buyer_client = Client.objects.create(
            name=payload.buyer_name,
            surname=payload.buyer_surname or "",
            phone_number=payload.buyer_phone or "",
            email=payload.buyer_email,
        )
        
        # 2. Procesar masajes y calcular precio
        baths = payload.baths or []
        if not baths:
            raise ValueError("Debe indicar al menos un tipo de baño/masaje")
        
        # Buscar los tipos de baños en la base de datos y calcular precio total
        final_price = Decimal("0")
        bath_type_details = []
        
        for br in baths:
            if isinstance(br, dict):
                # Convertir dict a StaffBathRequestDTO
                br = StaffBathRequestDTO(**br)
            
            br.validate()
            
            try:
                # Buscar el BathType existente en la base de datos
                bath_type = BathType.objects.get(
                    massage_type=br.massage_type,
                    massage_duration=br.minutes
                )
                
                # Calcular precio: bathtype.price x quantity
                bath_total_price = bath_type.price * br.quantity
                final_price += bath_total_price
                
                bath_type_details.append({
                    'bath_type': bath_type,
                    'quantity': br.quantity,
                    'massage_type': br.massage_type,
                    'duration': br.minutes
                })
                
            except BathType.DoesNotExist:
                raise ValueError(f"No existe el tipo de baño: {br.massage_type} de {br.minutes} minutos")
        
        # 3. Buscar producto existente con mismo precio y mismos BathTypes
        bath_types_signature = sorted([
            (detail['massage_type'], detail['duration'], detail['quantity']) 
            for detail in bath_type_details
        ])
        
        # Buscar productos con el mismo precio calculado
        candidates = Product.objects.filter(price=final_price)
        
        product = None
        for prod in candidates:
            # Obtener los bath_types del producto candidato
            prod_baths = list(prod.baths.values_list(
                'bath_type__massage_type', 
                'bath_type__massage_duration', 
                'quantity'
            ))
            prod_baths_signature = sorted(prod_baths)
            
            # Si coinciden exactamente los tipos de baño y cantidades
            if bath_types_signature == prod_baths_signature:
                product = prod
                break
        
        # 4. Si no existe producto, crear uno nuevo
        if not product:
            # Generar nombre descriptivo basado en los masajes
            massage_descriptions = []
            bath_descriptions = []
            
            # Mapeo de tipos de masaje a español
            massage_type_spanish = {
                'relax': 'Relajante',
                'rock': 'Piedras', 
                'exfoliation': 'Exfoliante',
                'none': 'Solo Baños'
            }
            
            for detail in bath_type_details:
                massage_type = detail['massage_type']
                duration = detail['duration']
                quantity = detail['quantity']
                
                # Traducir tipo de masaje al español
                spanish_type = massage_type_spanish.get(massage_type, massage_type.title())
                
                if massage_type == 'none':
                    # Para baños sin masaje
                    bath_descriptions.append(f"{quantity}x {spanish_type}")
                else:
                    # Para masajes con duración
                    massage_descriptions.append(f"{quantity}x {spanish_type} {duration}'")
            
            # Combinar descripciones de masajes y baños
            all_descriptions = massage_descriptions + bath_descriptions
            
            if all_descriptions:
                product_name = f"Cheque Regalo: {', '.join(all_descriptions)}"
            else:
                # Fallback si no hay descripciones
                product_name = f"Cheque Regalo - {payload.gift_name}"
            
            # Determinar si es solo baños sin masaje o incluye masajes
            has_massages = any(detail['massage_type'] != 'none' for detail in bath_type_details)
            
            product = Product.objects.create(
                name=product_name,
                description=f"Producto para cheque regalo: {payload.gift_name}",
                price=final_price,
                uses_capacity=True,
                uses_massagist=has_massages,
                visible=False,
            )
            
            # Crear los ProductBaths asociados
            for detail in bath_type_details:
                ProductBaths.objects.create(
                    product=product,
                    bath_type=detail['bath_type'],
                    quantity=detail['quantity']
                )
        
        # 5. Crear el gift voucher
        voucher_dto = GiftVoucherDTO(
            price=final_price,
            status='pending_payment',  # Estado inicial
            people=payload.people,
            buyer_client_id=buyer_client.id,
            product_id=product.id,
            recipients_email=payload.recipient_email or "",
            recipients_name=payload.recipient_name or "",
            recipients_surname=payload.recipient_surname or "",
            gift_name=payload.gift_name,
            gift_description=payload.gift_description or "",
        )
        
        return GiftVoucherManager.create_voucher(voucher_dto)

    # ------------------------------------------------------------------
    # Marcar cheque regalo como usado
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def mark_as_used(voucher_id: int) -> GiftVoucherDTO:
        """Marca un cheque regalo como usado."""
        try:
            voucher = GiftVoucher.objects.get(id=voucher_id)
            
            if voucher.status == 'used':
                raise ValueError(f"El cheque regalo #{voucher.code} ya está marcado como usado")
            
            if voucher.status != 'paid':
                raise ValueError(f"El cheque regalo #{voucher.code} debe estar pagado antes de poder ser usado")
            
            voucher.status = 'used'
            voucher.save(update_fields=['status'])
            
            return GiftVoucherManager._to_dto(voucher)
            
        except GiftVoucher.DoesNotExist:
            raise ValueError(f"No se encontró el cheque regalo con ID {voucher_id}")

