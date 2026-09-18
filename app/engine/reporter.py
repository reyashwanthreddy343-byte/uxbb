from typing import List, Dict, Any
from app.schemas.findings import RunReport, Finding, RegressionSummary, AccessibilityViolation
from app.schemas.run import StepEvent, FailureMemoryStats
from app.engine.clustering import root_cause_clusterer
from app.engine.failure_memory import failure_memory
from app.core.logger import logger

class DiagnosticReporter:
    """
    Assembles real model metrics, root-cause clusters, calibrated severity scores,
    and grounded explanations into the final RunReport.
    """
    
    def assemble_report(
        self,
        run_id: str,
        goal: str,
        target_url: str,
        platform: str,
        steps: List[StepEvent],
        raw_findings: List[Dict[str, Any]],
        regression_data: Dict[str, Any],
        a11y_violations: List[AccessibilityViolation],
        created_at: float,
        completed_at: float
    ) -> RunReport:
        
        # 1. Apply Root-Cause Clustering
        clustered_findings_dicts = root_cause_clusterer.cluster_findings(raw_findings)
        
        # 2. Build Finding Pydantic Objects
        finding_objs: List[Finding] = []
        for fd in clustered_findings_dicts:
            finding_objs.append(Finding(
                id=fd.get("id", f"find_{len(finding_objs)+1}"),
                step_number=fd.get("step_number", 1),
                finding_type=fd.get("finding_type", "friction"),
                severity_score=fd.get("severity_score", 0.5),
                confidence_score=fd.get("confidence_score", 0.9),
                cluster_id=fd.get("cluster_id", "cluster_1"),
                title=fd.get("title", "UI Friction Point"),
                explanation=fd.get("explanation", "Detected interaction resistance."),
                coordinates=fd.get("coordinates"),
                snapshot_url=fd.get("snapshot_url")
            ))
            
        # 3. Regression Summary
        regression = RegressionSummary(
            flagged=regression_data.get("flagged", False),
            baseline_run_id=regression_data.get("baseline_run_id"),
            anomaly_score=regression_data.get("anomaly_score", 0.0),
            backtrack_increase=regression_data.get("backtrack_increase", 0),
            duration_delta_sec=regression_data.get("duration_delta_sec", 0.0),
            details=regression_data.get("details", "")
        )
        
        # 4. Failure Memory Stats
        mem_stats_dict = failure_memory.get_memory_stats()
        mem_stats = FailureMemoryStats(
            runs_seen=mem_stats_dict["runs_seen"],
            detection_speed_curve=mem_stats_dict["detection_speed_curve"],
            recall_accuracy=mem_stats_dict["recall_accuracy"]
        )
        
        return RunReport(
            run_id=run_id,
            status="completed",
            goal=goal,
            target_url=target_url,
            platform=platform,
            steps=steps,
            findings=finding_objs,
            regression=regression,
            failure_memory=mem_stats,
            a11y_violations=a11y_violations,
            created_at=created_at,
            completed_at=completed_at
        )

diagnostic_reporter = DiagnosticReporter()
