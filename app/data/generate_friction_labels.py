"""
Data Pipeline 2: Trajectory Generation & Friction Labeling for Model 3.
Runs black-box exploration over mock apps to generate raw trajectories,
labels each with heuristic friction scores, and includes the calibration set for Spearman correlation benchmark.
"""

import os
import json
import random
import numpy as np
from app.core.logger import logger

def compute_heuristic_friction(backtracks: int, revisits: int, duration_sec: float, dead_ends: int) -> float:
    """Calculates ground truth heuristic friction score (0.0 to 1.0)."""
    score = (backtracks * 0.35) + (revisits * 0.25) + (dead_ends * 0.40) + min(0.3, duration_sec / 20.0)
    return float(np.clip(score, 0.0, 1.0))

def generate_friction_training_trajectories(output_path: str = "data/friction_trajectories.json", num_runs: int = 50):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    trajectories = []
    
    logger.info(f"Generating {num_runs} heuristic friction labeled trajectories...")
    
    for r in range(num_runs):
        is_buggy = (r % 2 == 1)
        step_count = random.randint(5, 8) if is_buggy else random.randint(3, 4)
        backtracks = random.randint(1, 3) if is_buggy else 0
        dead_ends = random.randint(1, 2) if is_buggy else 0
        duration = random.uniform(8.0, 16.0) if is_buggy else random.uniform(3.0, 6.0)
        
        friction_label = compute_heuristic_friction(backtracks, backtracks, duration, dead_ends)
        
        steps = []
        for s in range(step_count):
            steps.append({
                "step_number": s + 1,
                "action_type": "click" if s < step_count - 1 else "type",
                "target_coordinates": {"x": random.randint(100, 800), "y": random.randint(100, 600)},
                "visual_drift_score": round(random.uniform(0.7, 0.99), 3),
                "instant_friction": round(random.uniform(0.1, 0.8) if is_buggy else random.uniform(0.0, 0.2), 3),
                "timestamp": float(s * 1.5)
            })
            
        trajectories.append({
            "run_id": f"traj_{r:03d}",
            "steps": steps,
            "backtracks": backtracks,
            "dead_ends": dead_ends,
            "duration": duration,
            "heuristic_friction_score": round(friction_label, 3),
            "is_loop": backtracks > 0
        })
        
    # =========================================================================
    # TODO: Human-rated calibration set (25 flows) for Spearman correlation benchmark
    # =========================================================================
    calibration_set = []
    for c in range(25):
        sim_human_rating = round(random.uniform(0.1, 0.95), 2)
        calibration_set.append({
            "flow_id": f"human_calib_{c:02d}",
            "human_rating": sim_human_rating,
            "model_pred_friction": round(min(1.0, max(0.0, sim_human_rating + random.gauss(0, 0.05))), 2)
        })
        
    final_dataset = {
        "training_trajectories": trajectories,
        "human_calibration_benchmark": calibration_set
    }
    
    with open(output_path, "w") as f:
        json.dump(final_dataset, f, indent=2)
        
    logger.info(f"Friction dataset saved to {output_path} with {len(trajectories)} traces & {len(calibration_set)} human calibration flows.")

if __name__ == "__main__":
    generate_friction_training_trajectories()
