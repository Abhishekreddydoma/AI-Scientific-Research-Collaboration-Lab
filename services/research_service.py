"""Research service — business logic for research project management."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import ProjectNotFoundError
from app.core.logging import get_logger
from app.database.models.research_project import ResearchProject
from app.schemas.research import ResearchCreate, ResearchUpdate

logger = get_logger(__name__)


class ResearchService:
    """Service class for research project CRUD operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_project(self, payload: ResearchCreate) -> ResearchProject:
        """Create a new research project.

        Args:
            payload: Validated project creation data.

        Returns:
            The newly created ResearchProject ORM instance with status 'created'.
        """
        project = ResearchProject(
            user_id=payload.user_id,
            title=payload.title,
            research_question=payload.research_question,
            status="created",
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        logger.info(
            "Created research project id=%d title=%r user_id=%d",
            project.id,
            project.title,
            project.user_id,
        )
        return project

    def get_project(self, project_id: int) -> ResearchProject:
        """Retrieve a research project by ID.

        Args:
            project_id: The primary key of the project.

        Returns:
            The ResearchProject ORM instance.

        Raises:
            ProjectNotFoundError: If no project exists with the given ID.
        """
        project = (
            self.db.query(ResearchProject)
            .filter(ResearchProject.id == project_id)
            .first()
        )
        if not project:
            raise ProjectNotFoundError()
        return project

    def get_projects(
        self,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ResearchProject]:
        """List research projects, optionally filtered by user.

        Args:
            user_id: If provided, only return projects owned by this user.
            skip: Number of records to skip (pagination).
            limit: Maximum number of records to return.

        Returns:
            A list of ResearchProject ORM instances.
        """
        query = self.db.query(ResearchProject)
        if user_id is not None:
            query = query.filter(ResearchProject.user_id == user_id)
        return query.order_by(ResearchProject.created_at.desc()).offset(skip).limit(limit).all()

    def update_project(self, project_id: int, payload: ResearchUpdate) -> ResearchProject:
        """Partially update a research project.

        Args:
            project_id: The primary key of the project to update.
            payload: Partial update data — only non-None fields are applied.

        Returns:
            The updated ResearchProject ORM instance.

        Raises:
            ProjectNotFoundError: If no project exists with the given ID.
        """
        project = self.get_project(project_id)
        update_data = payload.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        self.db.commit()
        self.db.refresh(project)
        logger.info("Updated research project id=%d fields=%s", project.id, list(update_data.keys()))
        return project

    def delete_project(self, project_id: int) -> None:
        """Delete a research project and all its related records.

        Args:
            project_id: The primary key of the project to delete.

        Raises:
            ProjectNotFoundError: If no project exists with the given ID.
        """
        project = self.get_project(project_id)
        self.db.delete(project)
        self.db.commit()
        logger.info("Deleted research project id=%d", project_id)
