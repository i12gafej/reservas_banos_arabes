from reservations.models import Capacity
from reservations.dtos.capacity import CapacityDTO

class CapacityManager:
    """Gestor CRUD para Capacity."""

    @staticmethod
    def get_capacity(capacity_id: int) -> Capacity:
        return Capacity.objects.get(id=capacity_id)

    @staticmethod
    def update_capacity(capacity_id: int, dto: CapacityDTO) -> Capacity:
        dto.validate()
        cap = Capacity.objects.get(id=capacity_id)
        cap.value = dto.value
        cap.save()
        return cap
