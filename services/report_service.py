"""Report service — business logic for research report management."""

from typing import List

from sqlalchemy.orm import Session

from app.core.exceptions import ProjectNotFoundError, ReportNotFoundError
from app.core.logging import get_logger
from app.database.models.research_project import ResearchProject
from app.database.models.research_report import ResearchReport
from app.schemas.report import ResearchReportCreate

logger = get_logger(__name__)


class ReportService:
    """Service class for research report CRUD operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def _assert_project_exists(self, project_id: int) -> None:
        """Verify a project exists, raising ProjectNotFoundError if not."""
        project = self.db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
        if not project:
            raise ProjectNotFoundError()

    def create_report(self, project_id: int, payload: ResearchReportCreate) -> ResearchReport:
        """Create a research report for a project.

        Args:
            project_id: The ID of the parent research project.
            payload: Validated report creation data.

        Returns:
            The newly created ResearchReport ORM instance.

        Raises:
            ProjectNotFoundError: If the project does not exist.
        """
        self._assert_project_exists(project_id)

        report = ResearchReport(
            project_id=project_id,
            report_content=payload.report_content,
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        logger.info("Created research report id=%d project_id=%d", report.id, project_id)
        return report

    def get_report(self, project_id: int, report_id: int) -> ResearchReport:
        """Retrieve a specific research report.

        Args:
            project_id: The ID of the parent project.
            report_id: The ID of the report to retrieve.

        Returns:
            The ResearchReport ORM instance.

        Raises:
            ProjectNotFoundError: If the project does not exist.
            ReportNotFoundError: If the report does not exist or belongs to a different project.
        """
        self._assert_project_exists(project_id)
        report = (
            self.db.query(ResearchReport)
            .filter(ResearchReport.id == report_id, ResearchReport.project_id == project_id)
            .first()
        )
        if not report:
            raise ReportNotFoundError()
        return report

    def get_reports(self, project_id: int) -> List[ResearchReport]:
        """List all research reports for a project.

        Args:
            project_id: The ID of the parent project.

        Returns:
            A list of ResearchReport ORM instances ordered by creation time descending.

        Raises:
            ProjectNotFoundError: If the project does not exist.
        """
        self._assert_project_exists(project_id)
        return (
            self.db.query(ResearchReport)
            .filter(ResearchReport.project_id == project_id)
            .order_by(ResearchReport.created_at.desc())
            .all()
        )
