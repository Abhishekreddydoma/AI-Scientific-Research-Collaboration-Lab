"""Agent service — business logic for agent run management."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import AgentRunNotFoundError, ProjectNotFoundError
from app.core.logging import get_logger
from app.database.models.agent_run import AgentRun
from app.database.models.research_project import ResearchProject

logger = get_logger(__name__)


class AgentService:
    """Service class for agent run storage and retrieval.

    Agent run creation is an internal operation — not exposed via public API.
    The orchestration layer (LangGraph, future sprint) will call these methods.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_agent_run(
        self,
        project_id: int,
        agent_name: str,
        input_data: Optional[Dict[str, Any]] = None,
    ) -> AgentRun:
        """Create a new agent run record for a project.

        This is an internal method called by the orchestration layer.

        Args:
            project_id: The ID of the research project.
            agent_name: The name of the agent being run.
            input_data: Optional dictionary of input data (serialized to JSON).

        Returns:
            The newly created AgentRun ORM instance.

        Raises:
            ProjectNotFoundError: If the project does not exist.
        """
        project = self.db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
        if not project:
            raise ProjectNotFoundError()

        run = AgentRun(
            project_id=project_id,
            agent_name=agent_name,
            status="pending",
            input=json.dumps(input_data) if input_data else None,
            started_at=datetime.utcnow(),
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        logger.info(
            "Created agent run id=%d agent=%r project_id=%d",
            run.id,
            agent_name,
            project_id,
        )
        return run

    def get_agent_runs(self, project_id: int) -> List[AgentRun]:
        """List all agent runs for a project.

        Args:
            project_id: The ID of the research project.

        Returns:
            A list of AgentRun ORM instances ordered by start time descending.

        Raises:
            ProjectNotFoundError: If the project does not exist.
        """
        project = self.db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
        if not project:
            raise ProjectNotFoundError()

        return (
            self.db.query(AgentRun)
            .filter(AgentRun.project_id == project_id)
            .order_by(AgentRun.started_at.desc())
            .all()
        )

    def get_agent_run_by_name(self, project_id: int, agent_name: str) -> List[AgentRun]:
        """Retrieve all runs for a specific agent within a project.

        Args:
            project_id: The ID of the research project.
            agent_name: The name of the agent to filter by.

        Returns:
            A list of AgentRun ORM instances for the given agent.

        Raises:
            ProjectNotFoundError: If the project does not exist.
        """
        project = self.db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
        if not project:
            raise ProjectNotFoundError()

        return (
            self.db.query(AgentRun)
            .filter(AgentRun.project_id == project_id, AgentRun.agent_name == agent_name)
            .order_by(AgentRun.started_at.desc())
            .all()
        )

    def _deserialize_run(self, run: AgentRun) -> Dict[str, Any]:
        """Convert an AgentRun ORM instance to a dict with parsed JSON fields.

        Args:
            run: An AgentRun ORM instance.

        Returns:
            A dictionary representation with 'input' and 'output' parsed.
        """
        return {
            "id": run.id,
            "project_id": run.project_id,
            "agent_name": run.agent_name,
            "status": run.status,
            "input": json.loads(run.input) if run.input else None,
            "output": json.loads(run.output) if run.output else None,
            "started_at": run.started_at,
            "completed_at": run.completed_at,
        }
