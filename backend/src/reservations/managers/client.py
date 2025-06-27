from typing import List, Dict, Any
from collections import defaultdict

from django.db import transaction
from django.db.models import Q

from reservations.dtos.client import ClientDTO
from reservations.models import Client, Book, GiftVoucher


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
    # Unificación de clientes
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def unify_duplicate_clients() -> Dict[str, Any]:
        """
        Unifica clientes duplicados basándose en email y teléfono.
        
        Returns:
            Diccionario con estadísticas del proceso de unificación
        """
        # Encontrar duplicados por email y teléfono
        duplicate_groups = ClientManager._find_duplicate_clients()
        
        if not duplicate_groups:
            return {
                "success": True,
                "message": "No se encontraron clientes duplicados",
                "unified_groups": 0,
                "clients_removed": 0,
                "books_updated": 0,
                "gift_vouchers_updated": 0
            }
        
        total_books_updated = 0
        total_gift_vouchers_updated = 0
        total_clients_removed = 0
        
        # Procesar cada grupo de duplicados
        for group_key, clients in duplicate_groups.items():
            if len(clients) < 2:
                continue
                
            # Ordenar por ID (el más alto será el principal)
            clients.sort(key=lambda c: c.id, reverse=True)
            main_client = clients[0]  # Cliente principal (ID más alto)
            duplicate_clients = clients[1:]  # Clientes a eliminar
            
            # IDs de los clientes duplicados
            duplicate_ids = [c.id for c in duplicate_clients]
            
            # Actualizar referencias en Book
            books_updated = Book.objects.filter(client_id__in=duplicate_ids).update(client=main_client)
            total_books_updated += books_updated
            
            # Actualizar referencias en GiftVoucher
            gift_vouchers_updated = GiftVoucher.objects.filter(buyer_client_id__in=duplicate_ids).update(buyer_client=main_client)
            total_gift_vouchers_updated += gift_vouchers_updated
            
            # Eliminar clientes duplicados
            Client.objects.filter(id__in=duplicate_ids).delete()
            total_clients_removed += len(duplicate_ids)
        
        return {
            "success": True,
            "message": f"Unificación completada. {len(duplicate_groups)} grupos procesados.",
            "unified_groups": len(duplicate_groups),
            "clients_removed": total_clients_removed,
            "books_updated": total_books_updated,
            "gift_vouchers_updated": total_gift_vouchers_updated
        }

    @staticmethod
    def _find_duplicate_clients() -> Dict[str, List[Client]]:
        """
        Encuentra grupos de clientes duplicados basándose en email y teléfono.
        
        Returns:
            Diccionario donde la clave es "email|phone" y el valor es lista de clientes duplicados
        """
        # Filtrar clientes que tengan email Y teléfono (para evitar falsos positivos)
        clients_with_contact = Client.objects.filter(
            Q(email__isnull=False) & ~Q(email='') &
            Q(phone_number__isnull=False) & ~Q(phone_number='')
        ).order_by('email', 'phone_number')
        
        # Agrupar por email y teléfono
        groups = defaultdict(list)
        for client in clients_with_contact:
            # Normalizar email y teléfono para comparación
            email_key = client.email.lower().strip() if client.email else ""
            phone_key = client.phone_number.strip() if client.phone_number else ""
            
            # Solo agrupar si tanto email como teléfono tienen valor
            if email_key and phone_key:
                group_key = f"{email_key}|{phone_key}"
                groups[group_key].append(client)
        
        # Filtrar solo grupos con más de un cliente (duplicados)
        duplicate_groups = {k: v for k, v in groups.items() if len(v) > 1}
        
        return duplicate_groups

    @staticmethod
    def get_duplicate_clients_preview() -> Dict[str, Any]:
        """
        Obtiene una vista previa de los clientes duplicados sin realizar cambios.
        
        Returns:
            Diccionario con información de los duplicados encontrados
        """
        duplicate_groups = ClientManager._find_duplicate_clients()
        
        preview_data = {
            "total_groups": len(duplicate_groups),
            "total_duplicates": sum(len(clients) - 1 for clients in duplicate_groups.values()),
            "groups": []
        }
        
        for group_key, clients in duplicate_groups.items():
            email, phone = group_key.split('|')
            clients.sort(key=lambda c: c.id, reverse=True)
            main_client = clients[0]
            duplicates = clients[1:]
            
            # Contar referencias para cada cliente duplicado
            books_count = Book.objects.filter(client_id__in=[c.id for c in duplicates]).count()
            vouchers_count = GiftVoucher.objects.filter(buyer_client_id__in=[c.id for c in duplicates]).count()
            
            group_info = {
                "email": email,
                "phone": phone,
                "main_client": {
                    "id": main_client.id,
                    "name": main_client.name,
                    "surname": main_client.surname or "",
                    "created_at": main_client.created_at.isoformat() if main_client.created_at else None
                },
                "duplicates": [
                    {
                        "id": client.id,
                        "name": client.name,
                        "surname": client.surname or "",
                        "created_at": client.created_at.isoformat() if client.created_at else None
                    } for client in duplicates
                ],
                "books_to_update": books_count,
                "vouchers_to_update": vouchers_count
            }
            preview_data["groups"].append(group_info)
        
        return preview_data

    # ------------------------------------------------------------------
    # Búsqueda de clientes similares
    # ------------------------------------------------------------------

    @staticmethod
    def find_similar_clients(name: str = None, surname: str = None, email: str = None, phone_number: str = None) -> List[ClientDTO]:
        """
        Busca clientes similares basándose en los criterios proporcionados.
        
        Args:
            name: Nombre del cliente
            surname: Apellidos del cliente  
            email: Email del cliente
            phone_number: Número de teléfono del cliente
            
        Returns:
            Lista de clientes que coinciden con algún criterio
        """
        if not any([name, surname, email, phone_number]):
            return []
        
        query = Q()
        
        # Buscar por email exacto
        if email and email.strip():
            email_clean = email.strip().lower()
            query |= Q(email__iexact=email_clean)
        
        # Buscar por teléfono exacto
        if phone_number and phone_number.strip():
            phone_clean = phone_number.strip()
            query |= Q(phone_number__iexact=phone_clean)
        
        # Buscar por nombre y apellidos (combinación)
        if name and name.strip():
            name_clean = name.strip()
            name_query = Q(name__icontains=name_clean)
            
            if surname and surname.strip():
                surname_clean = surname.strip()
                name_query &= Q(surname__icontains=surname_clean)
            
            query |= name_query
        
        # Ejecutar consulta y obtener resultados únicos
        clients = Client.objects.filter(query).distinct().order_by('-created_at')[:20]  # Limitar a 20 resultados
        
        # Convertir a DTOs con información de coincidencias
        result = []
        for client in clients:
            dto = ClientManager._to_dto(client)
            # Agregar información sobre qué campos coinciden
            dto.match_info = ClientManager._get_match_info(client, name, surname, email, phone_number)
            result.append(dto)
        
        return result
    
    @staticmethod
    def _get_match_info(client: Client, search_name: str = None, search_surname: str = None, 
                       search_email: str = None, search_phone: str = None) -> Dict[str, bool]:
        """
        Determina qué campos del cliente coinciden con los criterios de búsqueda.
        
        Returns:
            Diccionario con información de coincidencias
        """
        matches = {
            'email': False,
            'phone': False,
            'name': False,
            'surname': False,
            'name_surname_combo': False
        }
        
        # Verificar coincidencia de email
        if search_email and client.email:
            matches['email'] = client.email.lower() == search_email.strip().lower()
        
        # Verificar coincidencia de teléfono
        if search_phone and client.phone_number:
            matches['phone'] = client.phone_number == search_phone.strip()
        
        # Verificar coincidencia de nombre
        if search_name and client.name:
            matches['name'] = search_name.strip().lower() in client.name.lower()
        
        # Verificar coincidencia de apellidos
        if search_surname and client.surname:
            matches['surname'] = search_surname.strip().lower() in client.surname.lower()
        
        # Verificar coincidencia de nombre + apellidos combinado
        if search_name and search_surname and client.name and client.surname:
            full_search = f"{search_name.strip()} {search_surname.strip()}".lower()
            full_client = f"{client.name} {client.surname}".lower()
            matches['name_surname_combo'] = full_search in full_client or full_client in full_search
        
        return matches

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
