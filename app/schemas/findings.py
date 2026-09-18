from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.run import StepEvent, FailureMemoryStats

class Finding(BaseModel):
    id: str
    step_number: int
    finding_type: str  # friction, regression, visual_drift, accessibility
    severity_score: float = Field(..., description="Severity 0.0-1.0 calibrated vs human ratings")
    confidence_score: float = Field(..., description="Model confidence 0.0-1.0")
    cluster_id: str = Field(..., description="Root-cause cluster identifier")
    title: str
    explanation: str = Field(..., description="Grounded explanation narrated from model outputs")
    coordinates: Optional[Dict[str, int]] = None
    snapshot_url: Optional[str] = None

class RegressionSummary(BaseModel):
    flagged: bool
    baseline_run_id: Optional[str] = None
    anomaly_score: float
    backtrack_increase: int
    duration_delta_sec: float
    details: str

class AccessibilityViolation(BaseModel):
    node_id: str
    role: str
    issue_type: str
    bounding_box: Dict[str, int]
    severity: str

class RunReport(BaseModel):
    run_id: str
    status: str  # queued, running, completed, failed
    goal: str
    target_url: str
    platform: str
    steps: List[StepEvent]
    findings: List[Finding]
    regression: RegressionSummary
    failure_memory: FailureMemoryStats
    a11y_violations: List[AccessibilityViolation] = []
    created_at: float
    completed_at: Optional[float] = None
