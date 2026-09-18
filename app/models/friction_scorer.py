import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import List, Dict, Any, Tuple
from app.core.logger import logger

class SequenceFrictionScorer(nn.Module):
    """
    Model 3: Sequence Friction & Backtrack Scorer.
    Inputs: Sequence of (element_embedding, action_type_onehot, time_delta, state_drift_val)
    Outputs:
    1. Friction Score Head (Regression 0.0 - 1.0)
    2. Backtrack/Loop Classifier Head (Binary Logits)
    3. Severity / Confidence Regression Head
    """
    
    ACTION_TYPES = ["click", "type", "scroll", "wait", "backtrack"]
    
    def __init__(self, feature_dim: int = 32, hidden_dim: int = 64):
        super().__init__()
        self.feature_dim = feature_dim
        self.hidden_dim = hidden_dim
        
        # Sequence GRU encoder
        self.gru = nn.GRU(
            input_size=feature_dim,
            hidden_size=hidden_dim,
            num_layers=2,
            batch_first=True,
            bidirectional=True
        )
        
        # Output Head 1: Friction Regression (0 to 1)
        self.friction_head = nn.Sequential(
            nn.Linear(hidden_dim * 2, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        
        # Output Head 2: Loop / Backtrack Classifier (Binary)
        self.backtrack_head = nn.Sequential(
            nn.Linear(hidden_dim * 2, 32),
            nn.ReLU(),
            nn.Linear(32, 2)
        )
        
        # Output Head 3: Severity & Confidence Estimator
        self.severity_head = nn.Sequential(
            nn.Linear(hidden_dim * 2, 32),
            nn.ReLU(),
            nn.Linear(32, 2), # [severity (0-1), confidence (0-1)]
            nn.Sigmoid()
        )

    def extract_step_features(self, step: Dict[str, Any], prev_step: Dict[str, Any] = None) -> np.ndarray:
        feat = np.zeros(self.feature_dim, dtype=np.float32)
        # Action one-hot
        action = step.get("action_type", "click")
        if action in self.ACTION_TYPES:
            feat[self.ACTION_TYPES.index(action)] = 1.0
            
        # Drift score
        feat[10] = float(step.get("visual_drift_score", 0.0))
        # Instant friction
        feat[11] = float(step.get("instant_friction", 0.0))
        # Coordinate normalized
        coords = step.get("target_coordinates") or {"x": 500, "y": 400}
        feat[12] = coords.get("x", 0) / 1280.0
        feat[13] = coords.get("y", 0) / 800.0
        
        # Time delta
        if prev_step:
            dt = step.get("timestamp", 0) - prev_step.get("timestamp", 0)
            feat[14] = float(np.clip(dt, 0.0, 10.0) / 10.0)
            
        return feat

    def score_trajectory(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates trajectory friction score, backtrack probability, and severity/confidence."""
        if not steps:
            return {
                "friction_score": 0.0,
                "is_loop": False,
                "loop_probability": 0.0,
                "severity_score": 0.0,
                "confidence_score": 0.95,
                "embedding": np.zeros(self.hidden_dim * 2, dtype=np.float32)
            }
            
        feat_list = []
        for i, s in enumerate(steps):
            prev = steps[i-1] if i > 0 else None
            feat_list.append(self.extract_step_features(s, prev))
            
        seq_tensor = torch.tensor(np.array(feat_list), dtype=torch.float32).unsqueeze(0)
        
        with torch.no_grad():
            out, hn = self.gru(seq_tensor)
            # Trajectory global pooled representation
            traj_emb = torch.mean(out, dim=1)  # shape: (1, hidden_dim * 2)
            
            friction = self.friction_head(traj_emb).item()
            loop_logits = self.backtrack_head(traj_emb)
            loop_prob = F.softmax(loop_logits, dim=-1)[0, 1].item()
            
            sev_conf = self.severity_head(traj_emb)[0]
            severity = sev_conf[0].item()
            confidence = sev_conf[1].item()
            
        # Programmatic heuristic boost if circular steps or repeated actions occur
        step_coords = [s.get("target_coordinates") for s in steps if s.get("target_coordinates")]
        duplicates = len(step_coords) - len(set([(c["x"], c["y"]) for c in step_coords]))
        if duplicates > 0:
            friction = min(1.0, friction + 0.25 * duplicates)
            loop_prob = min(1.0, loop_prob + 0.4)
            severity = min(1.0, severity + 0.3)
            
        return {
            "friction_score": round(friction, 3),
            "is_loop": loop_prob > 0.5,
            "loop_probability": round(loop_prob, 3),
            "severity_score": round(severity, 3),
            "confidence_score": round(confidence, 3),
            "embedding": traj_emb.squeeze(0).numpy()
        }
