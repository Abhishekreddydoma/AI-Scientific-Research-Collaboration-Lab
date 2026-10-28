"""Result service — business logic for research result management."""

import json
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.core.exceptions import ProjectNotFoundError, ResultNotFoundError
from app.core.logging import get_logger
from app.database.models.research_project import ResearchProject
from app.database.models.research_result import ResearchResult
from app.schemas.result import ResearchResultCreate

logger = get_logger(__name__)


class ResultService:
    """Service class for research result CRUD operations.

    Handles JSON serialization of the ``content`` field between the
    dict representation used in schemas and the JSON string stored in SQLite.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def _assert_project_exists(self, project_id: int) -> None:
        """Verify a project exists, raising ProjectNotFoundError if not."""
        project = self.db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
        if not project:
            raise ProjectNotFoundError()

    def create_result(self, project_id: int, payload: ResearchResultCreate) -> Dict[str, Any]:
        """Create a research result for a project.

        Args:
            project_id: The ID of the parent research project.
            payload: Validated result creation data.

        Returns:
            A dictionary representation of the created result with parsed content.

        Raises:
            ProjectNotFoundError: If the project does not exist.
        """
        self._assert_project_exists(project_id)

        result = ResearchResult(
            project_id=project_id,
            result_type=payload.result_type,
            title=payload.title,
            content=json.dumps(payload.content),
            source=payload.source,
        )
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        logger.info(
            "Created research result id=%d type=%r project_id=%d",
            result.id,
            result.result_type,
            project_id,
        )
        return self._deserialize(result)

    def get_result(self, project_id: int, result_id: int) -> Dict[str, Any]:
        """Retrieve a specific research result.

        Args:
            project_id: The ID of the parent project.
            result_id: The ID of the result to retrieve.

        Returns:
            A dictionary representation of the result with parsed content.

        Raises:
            ProjectNotFoundError: If the project does not exist.
            ResultNotFoundError: If the result does not exist or belongs to a different project.
        """
        self._assert_project_exists(project_id)
        result = (
            self.db.query(ResearchResult)
            .filter(ResearchResult.id == result_id, ResearchResult.project_id == project_id)
            .first()
        )
        if not result:
            raise ResultNotFoundError()
        return self._deserialize(result)

    def get_results(self, project_id: int) -> List[Dict[str, Any]]:
        """List all research results for a project.

        Args:
            project_id: The ID of the parent project.

        Returns:
            A list of result dictionaries ordered by creation time descending.

        Raises:
            ProjectNotFoundError: If the project does not exist.
        """
        self._assert_project_exists(project_id)
        results = (
            self.db.query(ResearchResult)
            .filter(ResearchResult.project_id == project_id)
            .order_by(ResearchResult.created_at.desc())
            .all()
        )
        return [self._deserialize(r) for r in results]

    @staticmethod
    def _deserialize(result: ResearchResult) -> Dict[str, Any]:
        """Convert a ResearchResult ORM instance to a dict with parsed content.

        Args:
            result: The ORM instance to convert.

        Returns:
            Dictionary with 'content' parsed from JSON string to dict.
        """
        return {
            "id": result.id,
            "project_id": result.project_id,
            "result_type": result.result_type,
            "title": result.title,
            "content": json.loads(result.content),
            "source": result.source,
            "created_at": result.created_at,
        }
