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

from reservations.dtos.book import BookDTO, StaffBathRequestDTO, BookLogDTO, BookDetailDTO, BookMassageUpdateDTO
from reservations.models import Book, Product, BathType, ProductBaths, Client, BookLogs, Admin, Agent, GiftVoucher, WebBooking


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
            observation=book.observation,
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
            observation=dto.observation or "",
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
            "observation": dto.observation,
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

    # ------------------------------------------------------------------
    # Gestión de BookLogs
    # ------------------------------------------------------------------

    @staticmethod
    def _booklog_to_dto(log: BookLogs) -> BookLogDTO:
        """Convierte un modelo BookLogs en BookLogDTO."""
        return BookLogDTO(
            id=log.id,
            book_id=log.book_id,
            datetime=log.datetime,
            comment=log.comment,
        )

    @staticmethod
    def get_book_logs(book_id: int) -> List[BookLogDTO]:
        """Obtiene todos los logs de una reserva."""
        logs = BookLogs.objects.filter(book_id=book_id).order_by('-datetime')
        return [BookManager._booklog_to_dto(log) for log in logs]

    @staticmethod
    @transaction.atomic
    def create_book_log(dto: BookLogDTO) -> BookLogDTO:
        """Crea un nuevo log para una reserva."""
        dto.validate_for_create()
        log = BookLogs.objects.create(
            book_id=dto.book_id,
            comment=dto.comment,
        )
        return BookManager._booklog_to_dto(log)

    # ------------------------------------------------------------------
    # Obtener detalles completos de una reserva
    # ------------------------------------------------------------------

    @staticmethod
    def _build_book_detail_dto(book: Book) -> BookDetailDTO:
        """Construye un BookDetailDTO a partir de un objeto Book."""
        # Obtener información del creador
        creator_type_name = "Sin creador"
        creator_name = "Sin creador"
        
        if book.creator_type and book.creator_id:
            try:
                model_class = book.creator_type.model_class()
                creator_obj = model_class.objects.get(id=book.creator_id)
                
                if isinstance(creator_obj, Admin):
                    creator_type_name = "Administrador"
                    creator_name = f"{creator_obj.name} {creator_obj.surname}"
                elif isinstance(creator_obj, Agent):
                    creator_type_name = "Agente"
                    creator_name = creator_obj.name
                elif isinstance(creator_obj, GiftVoucher):
                    creator_type_name = "Cheque regalo"
                    creator_name = f"Vale #{creator_obj.code} - {creator_obj.gift_name}"
                elif isinstance(creator_obj, WebBooking):
                    creator_type_name = "Reserva web"
                    creator_name = f"Reserva web #{creator_obj.id}"
            except Exception:
                # Si hay error al obtener el creador, mantener valores por defecto
                pass

        # Obtener información de los baños del producto
        product_baths = []
        if book.product:
            for product_bath in book.product.baths.select_related('bath_type').all():
                product_baths.append({
                    'massage_type': product_bath.bath_type.massage_type,
                    'massage_duration': product_bath.bath_type.massage_duration,
                    'quantity': product_bath.quantity,
                    'name': product_bath.bath_type.name,
                    'price': str(product_bath.bath_type.price),
                })

        return BookDetailDTO(
            id=book.id,
            internal_order_id=book.internal_order_id,
            booking_date=book.book_date,
            hour=book.hour,
            people=book.people,
            comment=book.comment,
            observation=book.observation,
            amount_paid=book.amount_paid,
            amount_pending=book.amount_pending,
            payment_date=book.payment_date,
            checked_in=book.checked_in,
            checked_out=book.checked_out,
            client_id=book.client_id,
            product_id=book.product_id,
            created_at=book.created_at,
            client_name=book.client.name,
            client_surname=book.client.surname or "",
            client_phone=book.client.phone_number or "",
            client_email=book.client.email or "",
            client_created_at=book.client.created_at,
            creator_type_name=creator_type_name,
            creator_name=creator_name,
            product_baths=product_baths,
        )

    @staticmethod
    def get_book_detail(book_id: int) -> BookDetailDTO:
        """Obtiene los detalles completos de una reserva incluyendo cliente y creador."""
        try:
            book = Book.objects.select_related('client', 'product', 'creator_type').get(id=book_id)
        except Book.DoesNotExist:
            raise ValueError(f"Reserva con ID {book_id} no encontrada")
        
        return BookManager._build_book_detail_dto(book)

    # ------------------------------------------------------------------
    # Helper para asegurar BathTypes necesarios
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

    # ------------------------------------------------------------------
    # Actualización de masajes en reserva existente
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def update_booking_massages(book_id: int, massages: BookMassageUpdateDTO) -> BookDetailDTO:
        """Actualiza los masajes de una reserva existente encontrando o creando un producto adecuado."""
        # Asegurar que existen todos los BathTypes necesarios
        BookManager.ensure_bath_types_exist()
        
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            raise ValueError(f"Reserva con ID {book_id} no encontrada")
            
        # Convertir masajes a formato StaffBathRequestDTO (incluye baños sin masaje)
        baths = massages.to_staff_bath_requests()
        
        # 1. Buscar los tipos de baños en la base de datos y calcular precio total
        final_price = Decimal("0")
        bath_type_details = []
        
        for br in baths:
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
        
        # 2. Buscar producto existente con mismo precio y mismos BathTypes
        bath_types_signature = sorted([
            (detail['massage_type'], detail['duration'], detail['quantity']) 
            for detail in bath_type_details
        ])
        
        # Buscar productos con el mismo precio calculado
        candidates = Product.objects.filter(price=final_price)
        
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
                # ¡Producto encontrado! Calcular nueva cantidad pendiente
                amount_already_paid = book.amount_paid
                new_amount_pending = final_price - amount_already_paid
                
                book.product = prod
                book.amount_pending = new_amount_pending
                book.save(update_fields=['product_id', 'amount_pending'])
                
                # Crear log con información detallada del cambio de precio
                if new_amount_pending < 0:
                    log_message = f"Masajes actualizados. Producto existente: {prod.name} (€{final_price}). Hay €{abs(new_amount_pending)} a devolver al cliente."
                elif new_amount_pending > 0:
                    log_message = f"Masajes actualizados. Producto existente: {prod.name} (€{final_price}). Quedan €{new_amount_pending} pendientes de pago."
                else:
                    log_message = f"Masajes actualizados. Producto existente: {prod.name} (€{final_price}). Pago completado."
                
                log_dto = BookLogDTO(book_id=book_id, comment=log_message)
                BookManager.create_book_log(log_dto)
                
                return BookManager._build_book_detail_dto(book)
        
        # 3. No existe producto, crear uno nuevo con visible=False
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
                if quantity == 1:
                    bath_descriptions.append(f"{quantity}x {spanish_type}")
                else:
                    bath_descriptions.append(f"{quantity}x {spanish_type}")
            else:
                # Para masajes con duración
                massage_descriptions.append(f"{quantity}x {spanish_type} {duration}'")
        
        # Combinar descripciones de masajes y baños
        all_descriptions = massage_descriptions + bath_descriptions
        
        if all_descriptions:
            product_name = ", ".join(all_descriptions)
        else:
            # Fallback si no hay descripciones
            product_name = f"Producto personalizado {book.book_date} {book.hour}"
        
        # Determinar si es solo baños sin masaje o incluye masajes
        has_massages = any(detail['massage_type'] != 'none' for detail in bath_type_details)
        
        if has_massages:
            product_description = "Producto personalizado con masajes"
        else:
            product_description = "Producto para baños sin masajes"
        
        product = Product.objects.create(
            name=product_name,
            description=product_description,
            price=final_price,
            uses_capacity=True,
            uses_massagist=has_massages,
            visible=False,
        )
        
        # Crear los ProductBaths asociados
        from reservations.models import ProductBaths
        for detail in bath_type_details:
            ProductBaths.objects.create(
                product=product,
                bath_type=detail['bath_type'],
                quantity=detail['quantity']
            )
        
        # 4. Actualizar la reserva con el nuevo producto
        amount_already_paid = book.amount_paid
        new_amount_pending = final_price - amount_already_paid
        
        book.product = product
        book.amount_pending = new_amount_pending
        book.save(update_fields=['product_id', 'amount_pending'])
        
        # 5. Crear log de la actualización con información detallada
        massage_details = [f"{detail['quantity']}x {detail['bath_type'].name}" for detail in bath_type_details]
        
        if new_amount_pending < 0:
            log_message = f"Masajes actualizados. Nuevo producto: {product.name} (€{final_price}). Incluye: {', '.join(massage_details)}. Hay €{abs(new_amount_pending)} a devolver al cliente."
        elif new_amount_pending > 0:
            log_message = f"Masajes actualizados. Nuevo producto: {product.name} (€{final_price}). Incluye: {', '.join(massage_details)}. Quedan €{new_amount_pending} pendientes de pago."
        else:
            log_message = f"Masajes actualizados. Nuevo producto: {product.name} (€{final_price}). Incluye: {', '.join(massage_details)}. Pago completado."
        
        log_dto = BookLogDTO(book_id=book_id, comment=log_message)
        BookManager.create_book_log(log_dto)
        
        return BookManager._build_book_detail_dto(book)

    # ------------------------------------------------------------------
    # Generar mensaje de log automático para cambios
    # ------------------------------------------------------------------

    @staticmethod
    def generate_change_log_message(original_data: dict, new_data: dict) -> str:
        """Genera automáticamente el mensaje de log basado en los cambios realizados."""
        messages = []

        # Cambio de fecha
        if original_data.get('booking_date') != new_data.get('booking_date'):
            old_date = original_data.get('booking_date', 'No especificada')
            new_date = new_data.get('booking_date', 'No especificada')
            messages.append(f"Fecha modificada del día {old_date} al día {new_date}")

        # Cambio de hora
        if original_data.get('hour') != new_data.get('hour'):
            old_hour = original_data.get('hour', 'No especificada')
            new_hour = new_data.get('hour', 'No especificada')
            messages.append(f"Hora modificada de {old_hour} a {new_hour}")

        # Cambio de personas
        if original_data.get('people') != new_data.get('people'):
            old_people = original_data.get('people', 0)
            new_people = new_data.get('people', 0)
            messages.append(f"Pasa de {old_people} a {new_people} personas")

        # Cambio de fecha de pago
        if original_data.get('payment_date') != new_data.get('payment_date'):
            old_payment = original_data.get('payment_date', 'Sin fecha')
            new_payment = new_data.get('payment_date', 'Sin fecha')
            messages.append(f"La fecha de pago cambia de {old_payment} a {new_payment}")

        # Cambio de importe pagado
        if original_data.get('amount_paid') != new_data.get('amount_paid'):
            old_paid = original_data.get('amount_paid', 0)
            new_paid = new_data.get('amount_paid', 0)
            messages.append(f"El importe pagado cambia de €{old_paid} a €{new_paid}")

        # Cambio de importe pendiente
        if original_data.get('amount_pending') != new_data.get('amount_pending'):
            old_pending = original_data.get('amount_pending', 0)
            new_pending = new_data.get('amount_pending', 0)
            messages.append(f"El importe a deber cambia de €{old_pending} a €{new_pending}")

        # Comparar masajes (esto requiere lógica más compleja para productos)
        # Por ahora lo dejamos simple, se podría extender más adelante
        if original_data.get('product_id') != new_data.get('product_id'):
            messages.append("Producto/masajes modificados")

        return ". ".join(messages) if messages else "Sin cambios detectados"

    # ------------------------------------------------------------------
    # Actualización con log automático
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def update_booking_with_log(dto: BookDTO, log_comment: str = None) -> BookDTO:
        """Actualiza una reserva y crea un log automático de los cambios."""
        # Obtener datos originales
        original_book = Book.objects.get(id=dto.id)
        original_data = {
            'booking_date': original_book.book_date,
            'hour': original_book.hour,
            'people': original_book.people,
            'amount_paid': original_book.amount_paid,
            'amount_pending': original_book.amount_pending,
            'payment_date': original_book.payment_date,
            'product_id': original_book.product_id,
        }

        # Actualizar reserva
        updated_dto = BookManager.update_booking(dto)

        # Preparar datos nuevos para comparación
        new_data = {
            'booking_date': dto.booking_date,
            'hour': dto.hour,
            'people': dto.people,
            'amount_paid': dto.amount_paid,
            'amount_pending': dto.amount_pending,
            'payment_date': dto.payment_date,
            'product_id': dto.product_id,
        }

        # Generar mensaje de log automático o usar el proporcionado
        if log_comment:
            log_message = log_comment
        else:
            log_message = BookManager.generate_change_log_message(original_data, new_data)

        # Crear log si hay cambios
        if log_message and log_message != "Sin cambios detectados":
            log_dto = BookLogDTO(
                book_id=dto.id,
                comment=log_message,
            )
            BookManager.create_book_log(log_dto)

        return updated_dto

    # ------------------------------------------------------------------
    # Comparación y actualización automática de masajes
    # ------------------------------------------------------------------

    @staticmethod
    def compare_and_update_massages(book_id: int, new_massage_data: dict, people: int) -> tuple[bool, dict]:
        """Compara los masajes actuales con los nuevos y actualiza si hay diferencias.
        Retorna (updated: bool, new_values: dict) donde new_values contiene los valores actualizados."""
        
        try:
            book = Book.objects.select_related('product').get(id=book_id)
        except Book.DoesNotExist:
            return False, {}
        
        # Obtener masajes actuales del producto
        current_massages = {
            'massage60Relax': 0,
            'massage60Piedra': 0,
            'massage60Exfol': 0,
            'massage30Relax': 0,
            'massage30Piedra': 0,
            'massage30Exfol': 0,
            'massage15Relax': 0,
        }
        
        if book.product and book.product.baths.exists():
            for product_bath in book.product.baths.select_related('bath_type').all():
                bath_type = product_bath.bath_type
                # Mapear de vuelta a los campos del formulario
                if bath_type.massage_duration == '60':
                    if bath_type.massage_type == 'relax':
                        current_massages['massage60Relax'] = product_bath.quantity
                    elif bath_type.massage_type == 'rock':
                        current_massages['massage60Piedra'] = product_bath.quantity
                    elif bath_type.massage_type == 'exfoliation':
                        current_massages['massage60Exfol'] = product_bath.quantity
                elif bath_type.massage_duration == '30':
                    if bath_type.massage_type == 'relax':
                        current_massages['massage30Relax'] = product_bath.quantity
                    elif bath_type.massage_type == 'rock':
                        current_massages['massage30Piedra'] = product_bath.quantity
                    elif bath_type.massage_type == 'exfoliation':
                        current_massages['massage30Exfol'] = product_bath.quantity
                elif bath_type.massage_duration == '15':
                    if bath_type.massage_type == 'relax':
                        current_massages['massage15Relax'] = product_bath.quantity
        
        # Comparar con los nuevos datos de masajes
        massage_fields = ['massage60Relax', 'massage60Piedra', 'massage60Exfol', 
                         'massage30Relax', 'massage30Piedra', 'massage30Exfol', 'massage15Relax']
        
        has_changes = False
        for field in massage_fields:
            new_value = new_massage_data.get(field, 0)
            current_value = current_massages[field]
            if new_value != current_value:
                has_changes = True
                break
        
        # Si hay cambios, actualizar masajes
        if has_changes:
            massage_dto = BookMassageUpdateDTO(
                massage60Relax=new_massage_data.get('massage60Relax', 0),
                massage60Piedra=new_massage_data.get('massage60Piedra', 0),
                massage60Exfol=new_massage_data.get('massage60Exfol', 0),
                massage30Relax=new_massage_data.get('massage30Relax', 0),
                massage30Piedra=new_massage_data.get('massage30Piedra', 0),
                massage30Exfol=new_massage_data.get('massage30Exfol', 0),
                massage15Relax=new_massage_data.get('massage15Relax', 0),
                people=people
            )
            
            # Actualizar masajes
            updated_detail = BookManager.update_booking_massages(book_id, massage_dto)
            
            # Refrescar el book desde la BD para obtener los valores actualizados
            book.refresh_from_db()
            
            # Devolver los valores que realmente se guardaron en la BD
            return True, {
                'product_id': book.product_id,
                'amount_pending': book.amount_pending
            }
        
        return False, {}
