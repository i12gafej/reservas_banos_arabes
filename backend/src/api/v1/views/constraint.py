from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from datetime import date, time
from typing import List

from api.v1.serializers.constraint import ConstraintSerializer
from reservations.models import Constraint
from reservations.managers.constraint import ConstraintManager
from reservations.dtos.constraint import ConstraintRangeDTO


class ConstraintViewSet(viewsets.ViewSet):
    """Endpoints para gestionar restricciones de reservas."""

    def list(self, request):
        """Obtiene todas las restricciones."""
        constraints = Constraint.objects.prefetch_related('constraintrange_set').all()
        serializer = ConstraintSerializer(constraints, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Obtiene una restricción específica."""
        try:
            constraint = Constraint.objects.prefetch_related('constraintrange_set').get(id=pk)
            serializer = ConstraintSerializer(constraint)
            return Response(serializer.data)
        except Constraint.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        """Crea una nueva restricción."""
        serializer = ConstraintSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        constraint = serializer.save()
        return Response(ConstraintSerializer(constraint).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        """Actualiza una restricción existente."""
        try:
            constraint = Constraint.objects.get(id=pk)
            serializer = ConstraintSerializer(constraint, data=request.data)
            serializer.is_valid(raise_exception=True)
            constraint = serializer.save()
            return Response(ConstraintSerializer(constraint).data)
        except Constraint.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        """Elimina una restricción."""
        try:
            constraint = Constraint.objects.get(id=pk)
            constraint.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Constraint.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='by-date/(?P<target_date>[^/.]+)')
    def by_date(self, request, target_date=None):
        """Obtiene la restricción para una fecha específica."""
        try:
            target_day = date.fromisoformat(target_date)
            constraint_dto = ConstraintManager.get_constraint_for_day(target_day)
            
            if constraint_dto is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
                
            # Convertir DTO a formato de respuesta
            response_data = {
                'id': constraint_dto.id,
                'day': constraint_dto.day.isoformat(),
                'ranges': [
                    {
                        'initial_time': r.initial_time.strftime('%H:%M:%S'),
                        'end_time': r.end_time.strftime('%H:%M:%S')
                    }
                    for r in constraint_dto.ranges
                ]
            }
            return Response(response_data)
            
        except ValueError:
            return Response(
                {"detail": "Formato de fecha inválido. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'], url_path='save-for-date')
    def save_for_date(self, request):
        """Guarda restricciones para una fecha específica desde celdas booleanas."""
        try:
            target_date_str = request.data.get('date')
            cells = request.data.get('cells', [])
            
            if not target_date_str:
                return Response(
                    {"detail": "Se requiere 'date'"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not isinstance(cells, list):
                return Response(
                    {"detail": "'cells' debe ser un array de booleanos"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            target_day = date.fromisoformat(target_date_str)
            
            # Convertir celdas a rangos
            ranges = ConstraintManager.ranges_from_time_cells(cells)
            
            if not ranges:
                # Si no hay rangos, eliminar restricción existente
                ConstraintManager.delete_constraint(target_day)
                return Response({'detail': 'Restricciones eliminadas'})
            
            # Guardar restricción
            constraint_dto = ConstraintManager.save_constraint(target_day, ranges)
            
            # Devolver respuesta
            response_data = {
                'id': constraint_dto.id,
                'day': constraint_dto.day.isoformat(),
                'ranges': [
                    {
                        'initial_time': r.initial_time.strftime('%H:%M:%S'),
                        'end_time': r.end_time.strftime('%H:%M:%S')
                    }
                    for r in constraint_dto.ranges
                ]
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response(
                {"detail": f"Error en formato de datos: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": f"Error al guardar restricción: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 