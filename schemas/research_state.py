"""Strongly-typed Pydantic schemas for the research workflow state.

These models form the backbone of the LangGraph state machine, the
A2A communication contract between specialized research agents, and the frontend.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


# ── Literature ─────────────────────────────────────────────────────────────────

class Paper(BaseModel):
    """A scientific paper retrieved from literature search."""
    paper_id: str
    title: str
    authors: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    abstract: Optional[str] = None
    url: Optional[str] = None
    source: str = "curated_corpus"
    doi: Optional[str] = None
    journal: Optional[str] = None
    citation_count: int = 0
    methodology: List[str] = Field(default_factory=list)
    key_findings: List[str] = Field(default_factory=list)


class LiteratureFindings(BaseModel):
    """Synthesized findings from peer-reviewed literature corpus."""
    total_papers_analyzed: int = 0
    total_citations: int = 0
    key_claims: List[str] = Field(default_factory=list)
    consensus_points: List[str] = Field(default_factory=list)
    contradictions_or_gaps: List[str] = Field(default_factory=list)
    common_methodologies: List[str] = Field(default_factory=list)


# ── Data & Statistics ──────────────────────────────────────────────────────────

class DescriptiveStat(BaseModel):
    mean: float
    std: float
    min: float
    max: float
    q25: float
    median: float
    q75: float
    count: int


class DatasetProfile(BaseModel):
    name: str
    source: str
    description: str
    num_rows: int
    num_columns: int
    columns: List[str] = Field(default_factory=list)
    missing_values: Dict[str, int] = Field(default_factory=dict)
    data_types: Dict[str, str] = Field(default_factory=dict)


class DataAnalysisResult(BaseModel):
    profile: DatasetProfile
    descriptive_statistics: Dict[str, DescriptiveStat] = Field(default_factory=dict)
    correlation_matrix: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    data_quality_score: float = 1.0
    key_insights: List[str] = Field(default_factory=list)


class CorrelationResult(BaseModel):
    var_x: str
    var_y: str
    pearson_r: float
    pearson_pvalue: float
    spearman_rho: float
    spearman_pvalue: float
    sample_size: int


class RegressionResult(BaseModel):
    dependent_var: str
    independent_vars: List[str]
    r_squared: float
    adj_r_squared: float
    f_statistic: float
    f_pvalue: float
    coefficients: Dict[str, float]
    p_values: Dict[str, float]
    standard_errors: Dict[str, float]
    confidence_intervals: Dict[str, List[float]]
    n_observations: int


# ── Hypothesis ─────────────────────────────────────────────────────────────────

class Hypothesis(BaseModel):
    id: str
    statement: str
    rationale: str
    independent_variables: List[str]
    dependent_variable: str
    expected_direction: Literal["positive", "negative", "non_linear", "moderated"] = "negative"
    test_method: str
    confidence_prior: float = 0.90
    status: Literal["proposed", "tested", "supported", "rejected"] = "proposed"


# ── Experiments ────────────────────────────────────────────────────────────────

class ExperimentResult(BaseModel):
    experiment_id: str
    hypothesis_id: str
    name: str
    description: str
    model_type: str
    dependent_variable: str
    independent_variables: List[str]
    sample_size: int
    r_squared: float
    f_statistic: float
    p_value: float
    coefficients: Dict[str, float] = Field(default_factory=dict)
    p_values: Dict[str, float] = Field(default_factory=dict)
    confidence_intervals: Dict[str, List[float]] = Field(default_factory=dict)
    standard_errors: Dict[str, float] = Field(default_factory=dict)
    conclusion: str
    supported: bool
    chart_data: Optional[Dict[str, Any]] = None


# ── Critic Review ──────────────────────────────────────────────────────────────

class ContradictionItem(BaseModel):
    topic: str = "Empirical Finding"
    claim_a: str = ""
    claim_b: str = ""
    resolution: str = "Further empirical investigation recommended"
    severity: Literal["low", "medium", "high"] = "low"


class CriticReview(BaseModel):
    review_id: str
    status: Literal["PASS", "REVISE"] = "PASS"
    overall_rigor_score: float
    statistical_validity_score: float
    literature_alignment_score: float
    methodological_robustness_score: float
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    detected_contradictions: List[ContradictionItem] = Field(default_factory=list)
    actionable_recommendations: List[str] = Field(default_factory=list)
    decision_rationale: str


# ── Research Plan ──────────────────────────────────────────────────────────────

class ResearchPlan(BaseModel):
    research_question: str
    domain: str
    objectives: List[str] = Field(default_factory=list)
    phases: List[str] = Field(default_factory=list)
    target_variables: List[str] = Field(default_factory=list)
    search_queries: List[str] = Field(default_factory=list)
    required_sample_size: int = 350


# ── Research Report ────────────────────────────────────────────────────────────

class ResearchReportSchema(BaseModel):
    title: str
    executive_summary: str
    literature_review: str
    methodology: str
    results: str
    discussion: str
    conclusions: str
    limitations: List[str] = Field(default_factory=list)
    future_work: List[str] = Field(default_factory=list)
    bibliography: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ── Master Research State ──────────────────────────────────────────────────────

class ResearchState(BaseModel):
    project_id: str = "1"
    run_id: str = "run-001"
    research_question: str = "Investigate relationships in the uploaded dataset"
    domain: str = "General empirical research"
    status: str = "in_progress"
    current_agent: Optional[str] = None
    revision_count: int = 0
    max_revisions: int = 2

    plan: Optional[ResearchPlan] = None
    literature_papers: List[Paper] = Field(default_factory=list)
    literature_findings: Optional[LiteratureFindings] = None
    data_analysis: Optional[DataAnalysisResult] = None
    hypotheses: List[Hypothesis] = Field(default_factory=list)
    experiments: List[ExperimentResult] = Field(default_factory=list)
    critic_reviews: List[CriticReview] = Field(default_factory=list)
    report: Optional[ResearchReportSchema] = None

    agent_activity: List[Dict[str, Any]] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
