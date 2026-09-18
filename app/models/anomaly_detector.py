import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Dict, Any, List, Optional
from app.core.logger import logger

class RegressionAnomalyDetector:
    """
    Model 4: Anomaly & Flow Regression Detector.
    Compares current run's trajectory embedding vs baseline run embedding via cosine distance.
    Also runs Isolation Forest over tabular metrics (backtrack_count, dead_ends, step_count, duration).
    """
    
    def __init__(self, anomaly_threshold: float = 0.35):
        self.anomaly_threshold = anomaly_threshold
        # Tabular isolation forest backup
        self.iso_forest = IsolationForest(contamination=0.1, random_state=42)
        # Synthetic baseline fit
        baseline_tabular = np.array([
            [3, 0, 0, 4.2],
            [4, 0, 0, 5.1],
            [5, 1, 0, 6.0],
            [3, 0, 0, 3.8],
            [4, 0, 0, 4.9]
        ])
        self.iso_forest.fit(baseline_tabular)

    def compute_embedding_distance(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Cosine distance between trajectory embeddings."""
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        cos_sim = np.dot(emb1, emb2) / (norm1 * norm2)
        return float(1.0 - cos_sim)

    def evaluate_regression(
        self,
        current_embedding: np.ndarray,
        current_metrics: Dict[str, Any],
        baseline_embedding: Optional[np.ndarray] = None,
        baseline_metrics: Optional[Dict[str, Any]] = None,
        baseline_run_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Flags if current run is an anomalous regression compared to baseline.
        """
        step_count = current_metrics.get("step_count", 0)
        backtracks = current_metrics.get("backtracks", 0)
        dead_ends = current_metrics.get("dead_ends", 0)
        duration = current_metrics.get("duration", 0.0)
        
        # 1. Tabular anomaly evaluation
        tab_features = np.array([[step_count, backtracks, dead_ends, duration]])
        iso_score = float(-self.iso_forest.score_samples(tab_features)[0]) # higher = more anomalous
        
        # 2. Embedding distance against baseline run
        if baseline_embedding is not None:
            emb_dist = self.compute_embedding_distance(current_embedding, baseline_embedding)
        else:
            emb_dist = 0.0
            
        # 3. Decision rule
        is_regression = False
        details = "Flow matches normal baseline trajectory."
        
        if baseline_metrics:
            base_steps = baseline_metrics.get("step_count", 3)
            base_backtracks = baseline_metrics.get("backtracks", 0)
            backtrack_inc = max(0, backtracks - base_backtracks)
            duration_delta = round(duration - baseline_metrics.get("duration", duration), 2)
        else:
            backtrack_inc = backtracks
            duration_delta = 0.0
            
        # If distance or backtracks exceed threshold
        anomaly_score = round(max(emb_dist, (backtrack_inc * 0.3) + (0.2 if iso_score > 0.6 else 0.0)), 3)
        if anomaly_score >= self.anomaly_threshold or backtrack_inc >= 1 or dead_ends >= 1:
            is_regression = True
            details = f"UX Flow Regression flagged: +{backtrack_inc} backtracks, +{duration_delta}s duration increase, embedding drift={round(emb_dist, 3)}."
            
        return {
            "flagged": is_regression,
            "baseline_run_id": baseline_run_id or "baseline_v1_run",
            "anomaly_score": anomaly_score,
            "backtrack_increase": backtrack_inc,
            "duration_delta_sec": duration_delta,
            "details": details
        }
