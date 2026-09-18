import pytest
import numpy as np
from PIL import Image
from app.models.element_detector import UIElementDetector
from app.models.visual_drift import SiameseVisualDrift
from app.models.friction_scorer import SequenceFrictionScorer
from app.models.anomaly_detector import RegressionAnomalyDetector

def test_model1_element_detector():
    detector = UIElementDetector()
    dummy_img = Image.new("RGB", (640, 640), color=(15, 23, 42))
    elements = detector.detect(dummy_img)
    assert isinstance(elements, list)
    assert len(elements) >= 0

def test_model2_visual_drift():
    drift_model = SiameseVisualDrift()
    img1 = Image.new("RGB", (224, 224), color=(20, 20, 20))
    img2 = Image.new("RGB", (224, 224), color=(20, 20, 20))
    score, verdict = drift_model.compare_states(img1, img2)
    assert 0.0 <= score <= 1.0
    assert verdict in ["same_state", "drifted_duplicate", "new_state"]

def test_model3_friction_scorer():
    scorer = SequenceFrictionScorer()
    steps = [
        {"step_number": 1, "action_type": "click", "visual_drift_score": 0.9, "target_coordinates": {"x": 100, "y": 100}, "timestamp": 1.0},
        {"step_number": 2, "action_type": "click", "visual_drift_score": 0.9, "target_coordinates": {"x": 100, "y": 100}, "timestamp": 2.0}, # duplicate click
        {"step_number": 3, "action_type": "backtrack", "visual_drift_score": 0.5, "target_coordinates": {"x": 100, "y": 100}, "timestamp": 3.0}
    ]
    res = scorer.score_trajectory(steps)
    assert "friction_score" in res
    assert 0.0 <= res["friction_score"] <= 1.0
    assert "severity_score" in res
    assert "confidence_score" in res
    assert res["is_loop"] is True # loop detected

def test_model4_anomaly_detector():
    detector = RegressionAnomalyDetector()
    current_emb = np.random.randn(128).astype(np.float32)
    base_emb = np.random.randn(128).astype(np.float32)
    
    current_metrics = {"step_count": 8, "backtracks": 3, "dead_ends": 1, "duration": 15.0}
    base_metrics = {"step_count": 3, "backtracks": 0, "dead_ends": 0, "duration": 4.0}
    
    res = detector.evaluate_regression(
        current_embedding=current_emb,
        current_metrics=current_metrics,
        baseline_embedding=base_emb,
        baseline_metrics=base_metrics
    )
    assert res["flagged"] is True
    assert res["anomaly_score"] > 0.0
