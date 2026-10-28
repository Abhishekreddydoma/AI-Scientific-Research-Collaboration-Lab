"""Multi-Agent Scientific Research Workflow Execution & Streaming Service.

Orchestrates the LangGraph multi-agent pipeline, saves results and runs to the
database, and streams real-time SSE execution events to connected frontends.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, Optional

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models.agent_run import AgentRun
from app.database.models.research_project import ResearchProject
from app.database.models.research_report import ResearchReport
from app.database.models.research_result import ResearchResult
from app.graph.workflow import build_research_graph
from app.graph.nodes import (
    research_lead_node,
    literature_node,
    data_node,
    hypothesis_node,
    experiment_node,
    critic_node,
    report_node,
)
from app.mcp.servers import setup_default_mcp_servers

logger = logging.getLogger(__name__)

# Ensure MCP servers are initialized
setup_default_mcp_servers()


class WorkflowService:
    """Service to coordinate LangGraph agent execution and SSE event streaming."""

    def __init__(self):
        self.graph = build_research_graph().compile()

    async def stream_workflow_execution(
        self,
        project_id: int,
        research_question: str,
        domain: str = "General empirical research",
        db: Optional[Session] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream real-time SSE events for a project's multi-agent workflow execution."""
        run_id = str(uuid.uuid4())
        logger.info(f"Starting research run {run_id} for project {project_id}")

        state_dict: Dict[str, Any] = {
            "project_id": str(project_id),
            "run_id": run_id,
            "research_question": research_question,
            "domain": domain,
            "status": "in_progress",
            "current_agent": None,
            "revision_count": 0,
            "max_revisions": 2,
            "plan": None,
            "literature_papers": [],
            "literature_findings": None,
            "data_analysis": None,
            "hypotheses": [],
            "experiments": [],
            "critic_reviews": [],
            "report": None,
            "agent_activity": [],
            "errors": [],
        }

        # Yield initial connected event
        yield self._format_sse("workflow_start", {
            "run_id": run_id,
            "project_id": project_id,
            "research_question": research_question,
            "timestamp": datetime.now().isoformat(),
        })

        nodes_sequence = [
            ("research_lead_node", research_lead_node, "research_lead", "Formulating scientific investigation plan"),
            ("literature_node", literature_node, "literature_agent", "Searching and synthesizing literature corpus"),
            ("data_node", data_node, "data_agent", "Profiling dataset and inferring variable roles"),
            ("hypothesis_node", hypothesis_node, "hypothesis_agent", "Formulating dataset- and question-grounded hypotheses"),
            ("experiment_node", experiment_node, "experiment_agent", "Executing dataset-selected statistical models"),
            ("critic_node", critic_node, "critic_agent", "Conducting adversarial peer review and verification"),
            ("report_node", report_node, "report_agent", "Compiling comprehensive peer-reviewed report"),
        ]

        try:
            for node_name, node_fn, agent_name, description in nodes_sequence:
                # Execute agent node
                node_output = await node_fn(state_dict)
                state_dict.update(node_output)

                activity = state_dict.get("agent_activity", [])
                latest_act = activity[-1] if activity else {"message": description}

                # Save AgentRun to DB if session available
                if db:
                    try:
                        ar = AgentRun(
                            project_id=int(project_id),
                            agent_name=agent_name,
                            status="completed",
                            input=json.dumps({"question": research_question}),
                            output=json.dumps(node_output, default=str),
                            started_at=datetime.now(),
                            completed_at=datetime.now(),
                        )
                        db.add(ar)
                        db.commit()
                    except Exception as db_err:
                        logger.error(f"Error persisting AgentRun: {db_err}")
                        if db:
                            db.rollback()

                # Yield node progress event
                yield self._format_sse("agent_event", {
                    "agent": agent_name,
                    "node": node_name,
                    "action": latest_act.get("action", description),
                    "message": latest_act.get("message", description),
                    "state_snapshot": {
                        "has_plan": state_dict.get("plan") is not None,
                        "papers_count": len(state_dict.get("literature_papers", [])),
                        "hypotheses_count": len(state_dict.get("hypotheses", [])),
                        "experiments_count": len(state_dict.get("experiments", [])),
                        "reviews_count": len(state_dict.get("critic_reviews", [])),
                        "has_report": state_dict.get("report") is not None,
                    },
                    "timestamp": datetime.now().isoformat(),
                })

            # Persist comprehensive final results into DB
            if db:
                self._persist_final_results(db, int(project_id), state_dict)

            # Yield workflow completed event with complete payload
            yield self._format_sse("workflow_complete", {
                "run_id": run_id,
                "project_id": project_id,
                "status": "completed",
                "final_state": state_dict,
                "timestamp": datetime.now().isoformat(),
            })

        except Exception as e:
            logger.exception(f"Workflow execution failed: {e}")
            yield self._format_sse("workflow_error", {
                "run_id": run_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            })

    def _persist_final_results(self, db: Session, project_id: int, state: Dict[str, Any]):
        """Save research results and final report to database tables."""
        pid = int(project_id)
        try:
            # 1. Update project status
            proj = db.query(ResearchProject).filter(ResearchProject.id == pid).first()
            if proj:
                proj.status = "completed"

            def to_serializable(obj):
                if hasattr(obj, "model_dump"):
                    return obj.model_dump()
                elif isinstance(obj, list):
                    return [to_serializable(x) for x in obj]
                elif isinstance(obj, dict):
                    return {k: to_serializable(v) for k, v in obj.items()}
                return obj

            # 2. Literature Result
            papers = state.get("literature_papers", [])
            findings = state.get("literature_findings")
            if papers or findings:
                res_lit = ResearchResult(
                    project_id=pid,
                    result_type="literature",
                    title="Synthesized Literature Review",
                    content=json.dumps({"papers": to_serializable(papers), "findings": to_serializable(findings)}, default=str),
                    source="literature_agent",
                )
                db.add(res_lit)

            # 3. Data Result
            data_analysis = state.get("data_analysis")
            if data_analysis:
                res_data = ResearchResult(
                    project_id=pid,
                    result_type="dataset",
                    title="Dataset Profile & Empirical Associations",
                    content=json.dumps(to_serializable(data_analysis), default=str),
                    source="data_agent",
                )
                db.add(res_data)

            # 4. Hypotheses Result
            hypotheses = state.get("hypotheses", [])
            if hypotheses:
                res_hyp = ResearchResult(
                    project_id=pid,
                    result_type="hypothesis",
                    title="Empirical Research Hypotheses",
                    content=json.dumps({"hypotheses": to_serializable(hypotheses)}, default=str),
                    source="hypothesis_agent",
                )
                db.add(res_hyp)

            # 5. Experiments Result
            experiments = state.get("experiments", [])
            if experiments:
                res_exp = ResearchResult(
                    project_id=pid,
                    result_type="experiment",
                    title="Dataset-Selected Statistical Models",
                    content=json.dumps({"experiments": to_serializable(experiments)}, default=str),
                    source="experiment_agent",
                )
                db.add(res_exp)

            # 6. Critic Review Result
            reviews = state.get("critic_reviews", [])
            if reviews:
                res_critic = ResearchResult(
                    project_id=pid,
                    result_type="critique",
                    title="Adversarial Peer Review Evaluation",
                    content=json.dumps({"reviews": to_serializable(reviews)}, default=str),
                    source="critic_agent",
                )
                db.add(res_critic)

            # 7. Final Report
            report = state.get("report")
            report_dict = to_serializable(report) if report else {}
            title = (report_dict.get("title") or "").strip()
            if report and title:
                exec_sum = report_dict.get("executive_summary", "")
                lit_rev = report_dict.get("literature_review", "")
                meth = report_dict.get("methodology", "")
                res = report_dict.get("results", "")
                disc = report_dict.get("discussion", "")
                conc = report_dict.get("conclusions", "")
                limitations = report_dict.get("limitations") or []
                future_work = report_dict.get("future_work") or []
                bibliography = report_dict.get("bibliography") or []
                lim_text = "\n".join(f"- {item}" for item in limitations) or "None reported."
                fut_text = "\n".join(f"- {item}" for item in future_work) or "None reported."
                bib_text = "\n".join(f"- {item}" for item in bibliography) or "No bibliographic records were retrieved."
                full_text = (
                    f"# {title}\n\n"
                    f"## Executive Summary\n{exec_sum}\n\n"
                    f"## Literature Review\n{lit_rev}\n\n"
                    f"## Methodology\n{meth}\n\n"
                    f"## Results\n{res}\n\n"
                    f"## Discussion\n{disc}\n\n"
                    f"## Conclusions\n{conc}\n\n"
                    f"## Limitations\n{lim_text}\n\n"
                    f"## Future Work\n{fut_text}\n\n"
                    f"## Bibliography\n{bib_text}"
                )
                rep_obj = ResearchReport(
                    project_id=pid,
                    report_content=full_text,
                )
                db.add(rep_obj)

            db.commit()
            logger.info(f"Successfully persisted results and report for project {pid}")
        except Exception as e:
            logger.exception(f"Error saving final results to DB: {e}")
            db.rollback()

    def _format_sse(self, event_type: str, data: Dict[str, Any]) -> str:
        """Format a message as SSE standard text."""
        return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


# Global workflow service instance
workflow_service = WorkflowService()
