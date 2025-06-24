from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from api.v1.serializers.book import BookingSerializer, BookLogSerializer, BookDetailSerializer
from reservations.managers.book import BookManager
from reservations.dtos.book import StaffBathRequestDTO, StaffBookingPayloadDTO


class BookViewSet(viewsets.ViewSet):
    """CRUD endpoints para reservas (Book) usando DTO + manager."""

    def list(self, request):
        dtos = BookManager.list_bookings()
        serializer = BookingSerializer(dtos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="by-date")
    def by_date(self, request):
        """Obtiene reservas por fecha específica."""
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({"detail": "Se requiere el parámetro 'date' (YYYY-MM-DD)"}, status=400)
        
        try:
            dtos = BookManager.list_bookings_by_date(date_str)
            serializer = BookingSerializer(dtos, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"detail": f"Error al obtener reservas: {str(e)}"}, status=400)

    def create(self, request):
        serializer = BookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dto_created = serializer.save()
        return Response(BookingSerializer(dto_created).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        dto = next((b for b in BookManager.list_bookings() if str(b.id) == str(pk)), None)
        if dto is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(BookingSerializer(dto).data)

    def update(self, request, pk=None):
        dto_current = next((b for b in BookManager.list_bookings() if str(b.id) == str(pk)), None)
        if dto_current is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = BookingSerializer(dto_current, data=request.data)
        serializer.is_valid(raise_exception=True)
        dto_updated = serializer.save()
        return Response(BookingSerializer(dto_updated).data)

    def destroy(self, request, pk=None):
        BookManager.delete_booking(int(pk))
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ------------------------------------------------------------------
    # Endpoint específico para reservas desde staff
    # ------------------------------------------------------------------

    @action(detail=False, methods=["post"], url_path="staff")
    def create_from_staff(self, request):
        data = request.data
        try:
            # Validar y construir el payload DTO
            payload = StaffBookingPayloadDTO(
                product_id=data.get("product_id"),
                baths=[StaffBathRequestDTO(**b) for b in data.get("baths", [])] if data.get("baths") else None,
                price=data.get("price"),
                name=data["name"],
                surname=data.get("surname", ""),
                phone=data["phone_number"],
                email=data.get("email", ""),
                date=data["date"],
                hour=data["hour"],
                people=data["people"],
                comment=data.get("comment", "")
            )
            payload.validate()
            dto_created = BookManager.create_booking_from_staff(
                product_id=payload.product_id,
                baths=payload.baths,
                price=payload.price,
                name=payload.name,
                surname=payload.surname,
                phone=payload.phone,
                email=payload.email,
                date=payload.date,
                hour=payload.hour,
                people=payload.people,
                comment=payload.comment or "",
            )
            return Response(BookingSerializer(dto_created).data, status=status.HTTP_201_CREATED)
        except KeyError as e:
            return Response({"detail": f"Campo requerido faltante: {e.args[0]}"}, status=400)
        except Exception as e:
            return Response({"detail": f"Error al crear reserva staff: {str(e)}"}, status=400)



    # ------------------------------------------------------------------
    # Endpoints para detalles de reserva y logs
    # NOTA: Solo se usa ID numérico, se eliminó soporte para internal_order_id
    # ------------------------------------------------------------------

    @action(detail=True, methods=["get"], url_path="detail")
    def get_detail(self, request, pk=None):
        """Obtiene los detalles completos de una reserva."""
        try:
            detail_dto = BookManager.get_book_detail(int(pk))
            serializer = BookDetailSerializer(detail_dto)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=404)
        except Exception as e:
            return Response({"detail": f"Error al obtener detalles: {str(e)}"}, status=400)

    @action(detail=True, methods=["put"], url_path="detail")
    def update_detail(self, request, pk=None):
        """Actualiza una reserva con detalles completos y genera log automático."""
        try:
            # Obtener los detalles actuales
            current_detail = BookManager.get_book_detail(int(pk))
            
            # Validar datos de entrada
            serializer = BookDetailSerializer(current_detail, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            # Actualizar con log automático
            updated_detail = serializer.save()
            
            # Devolver detalles actualizados
            return Response(BookDetailSerializer(updated_detail).data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=404)
        except Exception as e:
            return Response({"detail": f"Error al actualizar reserva: {str(e)}"}, status=400)

    @action(detail=True, methods=["get", "post"], url_path="logs")
    def manage_logs(self, request, pk=None):
        """Obtiene todos los logs de una reserva (GET) o crea un nuevo log (POST)."""
        if request.method == "GET":
            try:
                book_id = int(pk)
                log_dtos = BookManager.get_book_logs(book_id)
                serializer = BookLogSerializer(log_dtos, many=True)
                return Response(serializer.data)
            except Exception as e:
                return Response({"detail": f"Error al obtener logs: {str(e)}"}, status=400)
        
        elif request.method == "POST":
            try:
                book_id = int(pk)
                data = request.data.copy()
                data['book_id'] = book_id
                
                serializer = BookLogSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                log_dto = serializer.save()
                
                return Response(BookLogSerializer(log_dto).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"detail": f"Error al crear log: {str(e)}"}, status=400)
