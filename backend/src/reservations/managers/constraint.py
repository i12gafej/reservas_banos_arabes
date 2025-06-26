from datetime import date, time
from typing import List, Optional
from django.utils import timezone

from reservations.models import Constraint, ConstraintRange
from reservations.dtos.constraint import ConstraintDTO, ConstraintRangeDTO


class ConstraintManager:
    """Manager para gestionar restricciones de reservas."""

    @staticmethod
    def get_constraint_for_day(target_day: date) -> Optional[ConstraintDTO]:
        """
        Obtiene la restricción para un día específico.
        
        Args:
            target_day: Fecha para la cual obtener la restricción
            
        Returns:
            ConstraintDTO si existe restricción para ese día, None en caso contrario
        """
        try:
            constraint = Constraint.objects.get(day=target_day)
            ranges = constraint.constraintrange_set.all().order_by('initial_time')
            
            range_dtos = [
                ConstraintRangeDTO(
                    initial_time=r.initial_time,
                    end_time=r.end_time
                )
                for r in ranges
            ]
            
            return ConstraintDTO(
                id=constraint.id,
                day=constraint.day,
                ranges=range_dtos
            )
        except Constraint.DoesNotExist:
            return None

    @staticmethod
    def save_constraint(target_day: date, ranges: List[ConstraintRangeDTO]) -> ConstraintDTO:
        """
        Guarda o actualiza una restricción para un día específico.
        
        Args:
            target_day: Fecha para la restricción
            ranges: Lista de rangos de restricción
            
        Returns:
            ConstraintDTO con la restricción guardada
        """
        # Obtener o crear la restricción
        constraint, created = Constraint.objects.get_or_create(
            day=target_day,
            defaults={'created_at': timezone.now()}
        )
        
        # Eliminar rangos existentes
        constraint.constraintrange_set.all().delete()
        
        # Crear nuevos rangos
        for range_dto in ranges:
            ConstraintRange.objects.create(
                constraint=constraint,
                initial_time=range_dto.initial_time,
                end_time=range_dto.end_time
            )
        
        # Devolver DTO actualizado
        return ConstraintManager.get_constraint_for_day(target_day)

    @staticmethod
    def delete_constraint(target_day: date) -> bool:
        """
        Elimina una restricción para un día específico.
        
        Args:
            target_day: Fecha de la restricción a eliminar
            
        Returns:
            True si se eliminó la restricción, False si no existía
        """
        try:
            constraint = Constraint.objects.get(day=target_day)
            constraint.delete()
            return True
        except Constraint.DoesNotExist:
            return False

    @staticmethod
    def get_all_constraints() -> List[ConstraintDTO]:
        """
        Obtiene todas las restricciones ordenadas por fecha.
        
        Returns:
            Lista de ConstraintDTO
        """
        constraints = Constraint.objects.all().order_by('day')
        result = []
        
        for constraint in constraints:
            ranges = constraint.constraintrange_set.all().order_by('initial_time')
            range_dtos = [
                ConstraintRangeDTO(
                    initial_time=r.initial_time,
                    end_time=r.end_time
                )
                for r in ranges
            ]
            
            result.append(ConstraintDTO(
                id=constraint.id,
                day=constraint.day,
                ranges=range_dtos
            ))
        
        return result

    @staticmethod
    def ranges_from_time_cells(cells: List[bool], start_hour: int = 10, step_minutes: int = 30) -> List[ConstraintRangeDTO]:
        """
        Convierte un array de celdas booleanas a rangos de restricción.
        
        Args:
            cells: Array de booleanos donde True indica restricción
            start_hour: Hora de inicio (por defecto 10)
            step_minutes: Minutos por paso (por defecto 30)
            
        Returns:
            Lista de ConstraintRangeDTO
        """
        ranges = []
        i = 0
        
        while i < len(cells):
            if cells[i]:  # Si la celda está marcada como restricción
                # Encontrar el inicio del rango
                start_minutes = start_hour * 60 + i * step_minutes
                start_time = time(
                    hour=start_minutes // 60,
                    minute=start_minutes % 60
                )
                
                # Encontrar el final del rango
                j = i
                while j < len(cells) and cells[j]:
                    j += 1
                
                end_minutes = start_hour * 60 + j * step_minutes
                end_time = time(
                    hour=end_minutes // 60,
                    minute=end_minutes % 60
                )
                
                ranges.append(ConstraintRangeDTO(
                    initial_time=start_time,
                    end_time=end_time
                ))
                
                i = j
            else:
                i += 1
        
        return ranges

    @staticmethod
    def time_cells_from_ranges(ranges: List[ConstraintRangeDTO], num_cells: int = 25, start_hour: int = 10, step_minutes: int = 30) -> List[bool]:
        """
        Convierte rangos de restricción a un array de celdas booleanas.
        
        Args:
            ranges: Lista de ConstraintRangeDTO
            num_cells: Número de celdas (por defecto 25)
            start_hour: Hora de inicio (por defecto 10)
            step_minutes: Minutos por paso (por defecto 30)
            
        Returns:
            Array de booleanos donde True indica restricción
        """
        cells = [False] * num_cells
        
        for range_dto in ranges:
            # Convertir tiempos a índices
            start_minutes = range_dto.initial_time.hour * 60 + range_dto.initial_time.minute
            end_minutes = range_dto.end_time.hour * 60 + range_dto.end_time.minute
            
            start_index = (start_minutes - start_hour * 60) // step_minutes
            end_index = (end_minutes - start_hour * 60) // step_minutes
            
            # Marcar celdas como restringidas
            for i in range(max(0, start_index), min(num_cells, end_index)):
                cells[i] = True
        
        return cells

