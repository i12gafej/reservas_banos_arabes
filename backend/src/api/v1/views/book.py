from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from api.v1.serializers.book import BookingSerializer, BookLogSerializer, BookDetailSerializer, BookMassageUpdateSerializer
from reservations.managers.book import BookManager
from reservations.dtos.book import StaffBathRequestDTO, StaffBookingPayloadDTO


@method_decorator(csrf_exempt, name='dispatch')
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

    @action(detail=True, methods=["get", "put", "options"], url_path="detail")
    def manage_detail(self, request, pk=None):
        """Obtiene los detalles completos de una reserva (GET) o actualiza una reserva (PUT)."""
        # Agregar headers CORS y logging para debug
        from django.http import JsonResponse
        import json
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info(f"manage_detail called with method: {request.method}, pk: {pk}")
        logger.info(f"Request data: {request.data if hasattr(request, 'data') else 'No data'}")
        
        # Manejar CORS preflight requests
        if request.method == "OPTIONS":
            response = Response(status=200)
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, PUT, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            response["Access-Control-Max-Age"] = "86400"
            return response
        
        if request.method == "GET":
            try:
                detail_dto = BookManager.get_book_detail(int(pk))
                serializer = BookDetailSerializer(detail_dto)
                response = Response(serializer.data)
                # Agregar headers CORS explícitos
                response["Access-Control-Allow-Origin"] = "*"
                response["Access-Control-Allow-Methods"] = "GET, PUT, OPTIONS"
                response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
                return response
            except ValueError as e:
                response = Response({"detail": str(e)}, status=404)
                response["Access-Control-Allow-Origin"] = "*"
                return response
            except Exception as e:
                logger.error(f"Error en GET detail: {str(e)}")
                response = Response({"detail": f"Error al obtener detalles: {str(e)}"}, status=400)
                response["Access-Control-Allow-Origin"] = "*"
                return response
        
        elif request.method == "PUT":
            try:
                logger.info(f"Processing PUT request for book {pk}")
                
                # Obtener los detalles actuales
                current_detail = BookManager.get_book_detail(int(pk))
                
                # Validar datos de entrada
                logger.info(f"Validating data with serializer...")
                serializer = BookDetailSerializer(current_detail, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                
                # Actualizar con log automático
                logger.info(f"Saving updated details...")
                updated_detail = serializer.save()
                
                # Devolver detalles actualizados
                response_data = BookDetailSerializer(updated_detail).data
                response = Response(response_data)
                # Agregar headers CORS explícitos
                response["Access-Control-Allow-Origin"] = "*"
                response["Access-Control-Allow-Methods"] = "GET, PUT, OPTIONS"
                response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
                logger.info(f"PUT request completed successfully")
                return response
            except ValueError as e:
                logger.error(f"ValueError en PUT detail: {str(e)}")
                response = Response({"detail": str(e)}, status=404)
                response["Access-Control-Allow-Origin"] = "*"
                return response
            except Exception as e:
                logger.error(f"Error general en PUT detail: {str(e)}")
                response = Response({"detail": f"Error al actualizar reserva: {str(e)}"}, status=400)
                response["Access-Control-Allow-Origin"] = "*"
                return response

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

    @action(detail=True, methods=["put"], url_path="massages")
    def update_massages(self, request, pk=None):
        """Actualiza los masajes de una reserva existente."""
        try:
            # Obtener los detalles actuales para usar como instancia
            current_detail = BookManager.get_book_detail(int(pk))
            
            # Validar datos de entrada
            serializer = BookMassageUpdateSerializer(current_detail, data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Actualizar masajes
            updated_detail = serializer.save()
            
            # Devolver detalles actualizados
            return Response(BookDetailSerializer(updated_detail).data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=404)
        except Exception as e:
            return Response({"detail": f"Error al actualizar masajes: {str(e)}"}, status=400)

    @action(detail=True, methods=["get"], url_path="test")
    def test_endpoint(self, request, pk=None):
        """Endpoint de prueba para verificar que el routing funciona."""
        response = Response({
            "message": f"Test endpoint working for book {pk}",
            "method": request.method,
            "user": str(request.user),
            "data": request.data if hasattr(request, 'data') else None
        })
        response["Access-Control-Allow-Origin"] = "*"
        return response
