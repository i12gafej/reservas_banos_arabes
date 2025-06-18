from typing import List

from django.db import transaction

from reservations.dtos.agent import AgentDTO
from reservations.models import Agent


class AgentManager:
    """Gestor CRUD para agentes."""

    # ------------------------------------------------------------------
    # Crear
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def create_agent(dto: AgentDTO) -> AgentDTO:
        dto.validate_for_create()
        agent = Agent.objects.create(
            name=dto.name,
            platform=dto.platform or "",
            description=dto.description or "",
        )
        return AgentManager._to_dto(agent)

    # ------------------------------------------------------------------
    # Actualizar
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def update_agent(dto: AgentDTO) -> AgentDTO:
        dto.validate_for_update()
        agent = Agent.objects.get(id=dto.id)

        fields_map = {
            "name": dto.name,
            "platform": dto.platform,
            "description": dto.description,
        }
        changed_fields = []
        for field, value in fields_map.items():
            if value is not None:
                setattr(agent, field, value)
                changed_fields.append(field)
        if changed_fields:
            agent.save(update_fields=changed_fields)
        return AgentManager._to_dto(agent)

    # ------------------------------------------------------------------
    # Listar
    # ------------------------------------------------------------------

    @staticmethod
    def list_agents() -> List[AgentDTO]:
        return [AgentManager._to_dto(a) for a in Agent.objects.all().order_by("name")]

    # ------------------------------------------------------------------
    # Eliminar
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def delete_agent(agent_id: int) -> None:
        Agent.objects.filter(id=agent_id).delete()

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    @staticmethod
    def _to_dto(agent: Agent) -> AgentDTO:
        return AgentDTO(
            id=agent.id,
            name=agent.name,
            platform=agent.platform,
            description=agent.description,
            created_at=None,  
        )
