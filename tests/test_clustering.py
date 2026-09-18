import pytest
from app.engine.clustering import RootCauseClusterer

def test_root_cause_clustering_collapses_symptoms():
    """
    Asserts that multiple similar friction symptoms occurring near the same
    modal / coordinates collapse into common root cause clusters.
    """
    clusterer = RootCauseClusterer()
    
    # 4 synthetic findings at similar modal coordinates
    findings = [
        {"id": "f1", "step_number": 2, "severity_score": 0.8, "coordinates": {"x": 420, "y": 380}, "title": "Shift"},
        {"id": "f2", "step_number": 2, "severity_score": 0.85, "coordinates": {"x": 425, "y": 385}, "title": "Lag"},
        {"id": "f3", "step_number": 3, "severity_score": 0.75, "coordinates": {"x": 422, "y": 382}, "title": "Occlusion"},
        {"id": "f4", "step_number": 5, "severity_score": 0.2, "coordinates": {"x": 80, "y": 50}, "title": "Header link"}
    ]
    
    clustered = clusterer.cluster_findings(findings)
    assert len(clustered) == 4
    for f in clustered:
        assert "cluster_id" in f
        
    # First 3 should share the same cluster
    assert clustered[0]["cluster_id"] == clustered[1]["cluster_id"]
    assert clustered[0]["cluster_id"] == clustered[2]["cluster_id"]
