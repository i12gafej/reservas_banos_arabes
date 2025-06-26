from django.db.models import Q
from typing import List, Dict, Any, Optional
from reservations.models import Client, Book, GiftVoucher


class GeneralSearchService:
    """Servicio para realizar búsquedas generales en la base de datos."""
    
    @staticmethod
    def search(term: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Busca un término en clientes, reservas y cheques regalo.
        
        Args:
            term: Término de búsqueda
            
        Returns:
            Diccionario con los resultados organizados por tipo
        """
        if not term or len(term.strip()) < 2:
            return {
                'clients': [],
                'bookings': [],
                'gift_vouchers': []
            }
        
        term = term.strip()
        
        # Buscar en clientes
        clients = GeneralSearchService._search_clients(term)
        
        # Buscar en reservas
        bookings = GeneralSearchService._search_bookings(term)
        
        # Buscar en cheques regalo
        gift_vouchers = GeneralSearchService._search_gift_vouchers(term)
        
        return {
            'clients': clients,
            'bookings': bookings,
            'gift_vouchers': gift_vouchers
        }
    
    @staticmethod
    def _search_clients(term: str) -> List[Dict[str, Any]]:
        """Busca en la tabla de clientes."""
        query = Q()
        
        # Buscar por nombre, apellidos, teléfono, email
        query |= Q(name__icontains=term)
        query |= Q(surname__icontains=term)
        query |= Q(phone_number__icontains=term)
        query |= Q(email__icontains=term)
        
        # Si el término es numérico, buscar también por ID
        if term.isdigit():
            query |= Q(id=int(term))
        
        clients = Client.objects.filter(query).order_by('-created_at')[:10]
        
        return [
            {
                'id': client.id,
                'name': client.name,
                'surname': client.surname or '',
                'phone_number': client.phone_number or '',
                'email': client.email or '',
                'created_at': client.created_at.isoformat() if client.created_at else None,
                'type': 'client',
                'display_text': f"{client.name} {client.surname or ''}".strip(),
                'secondary_text': f"Tel: {client.phone_number or 'N/A'} | Email: {client.email or 'N/A'}"
            }
            for client in clients
        ]
    
    @staticmethod
    def _search_bookings(term: str) -> List[Dict[str, Any]]:
        """Busca en la tabla de reservas."""
        query = Q()
        
        # Buscar por ID interno de pedido
        query |= Q(internal_order_id__icontains=term)
        
        # Buscar por datos del cliente
        query |= Q(client__name__icontains=term)
        query |= Q(client__surname__icontains=term)
        query |= Q(client__phone_number__icontains=term)
        query |= Q(client__email__icontains=term)
        
        # Si el término es numérico, buscar también por ID de reserva
        if term.isdigit():
            query |= Q(id=int(term))
            query |= Q(client__id=int(term))
        
        bookings = Book.objects.select_related('client', 'product').filter(query).order_by('-created_at')[:10]
        
        return [
            {
                'id': booking.id,
                'internal_order_id': booking.internal_order_id,
                'book_date': booking.book_date.isoformat() if booking.book_date else None,
                'hour': str(booking.hour) if booking.hour else None,
                'people': booking.people,
                'client': {
                    'id': booking.client.id,
                    'name': booking.client.name,
                    'surname': booking.client.surname or '',
                    'phone_number': booking.client.phone_number or '',
                    'email': booking.client.email or '',
                },
                'product_name': booking.product.name if booking.product else '',
                'amount_paid': str(booking.amount_paid),
                'amount_pending': str(booking.amount_pending),
                'checked_in': booking.checked_in,
                'checked_out': booking.checked_out,
                'type': 'booking',
                'display_text': f"Reserva #{booking.internal_order_id} - {booking.client.name} {booking.client.surname or ''}".strip(),
                'secondary_text': f"Fecha: {booking.book_date} | Hora: {booking.hour} | {booking.people} personas"
            }
            for booking in bookings
        ]
    
    @staticmethod
    def _search_gift_vouchers(term: str) -> List[Dict[str, Any]]:
        """Busca en la tabla de cheques regalo."""
        query = Q()
        
        # Buscar por código
        query |= Q(code__icontains=term)
        
        # Buscar por datos del destinatario
        query |= Q(recipients_email__icontains=term)
        query |= Q(recipients_name__icontains=term)
        query |= Q(recipients_surname__icontains=term)
        
        # Buscar por datos del comprador
        query |= Q(buyer_client__name__icontains=term)
        query |= Q(buyer_client__surname__icontains=term)
        query |= Q(buyer_client__phone_number__icontains=term)
        query |= Q(buyer_client__email__icontains=term)
        
        # Si el término es numérico, buscar también por ID
        if term.isdigit():
            query |= Q(id=int(term))
            query |= Q(buyer_client__id=int(term))
        
        gift_vouchers = GiftVoucher.objects.select_related('buyer_client', 'product').filter(query).order_by('-created_at')[:10]
        
        return [
            {
                'id': voucher.id,
                'code': voucher.code,
                'price': str(voucher.price),
                'used': voucher.used,
                'bought_date': voucher.bought_date.isoformat() if voucher.bought_date else None,
                'recipient': {
                    'name': voucher.recipients_name or '',
                    'surname': voucher.recipients_surname or '',
                    'email': voucher.recipients_email or '',
                },
                'buyer_client': {
                    'id': voucher.buyer_client.id,
                    'name': voucher.buyer_client.name,
                    'surname': voucher.buyer_client.surname or '',
                    'phone_number': voucher.buyer_client.phone_number or '',
                    'email': voucher.buyer_client.email or '',
                },
                'product_name': voucher.product.name if voucher.product else '',
                'gift_name': voucher.gift_name or '',
                'type': 'gift_voucher',
                'display_text': f"Cheque #{voucher.code} - {voucher.gift_name or 'Sin nombre'}",
                'secondary_text': f"Comprador: {voucher.buyer_client.name} {voucher.buyer_client.surname or ''}".strip() + (f" | Destinatario: {voucher.recipients_name or ''} {voucher.recipients_surname or ''}".strip() if voucher.recipients_name else "")
            }
            for voucher in gift_vouchers
        ]
    
    @staticmethod
    def get_client_data_for_autocomplete(client_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene los datos de un cliente para autocompletar el formulario.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Datos del cliente o None si no existe
        """
        try:
            client = Client.objects.get(id=client_id)
            return {
                'name': client.name,
                'surname': client.surname or '',
                'phone_number': client.phone_number or '',
                'email': client.email or '',
            }
        except Client.DoesNotExist:
            return None
