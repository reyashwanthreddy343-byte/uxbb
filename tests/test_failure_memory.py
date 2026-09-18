import pytest
import numpy as np
from app.engine.failure_memory import FailureMemoryEngine

def test_failure_memory_indexing_and_top_k_recall():
    """
    Verifies that a known high-friction / regression trajectory is indexed
    and successfully retrieved in top-k nearest neighbor queries.
    """
    memory = FailureMemoryEngine(dim=64)
    
    # Create distinct risky vector
    risky_vec = np.zeros(64, dtype=np.float32)
    risky_vec[0] = 1.0
    
    # Index normal runs
    for i in range(5):
        normal_vec = np.random.randn(64).astype(np.float32)
        memory.record_run(f"norm_{i}", normal_vec, friction_score=0.1, is_regression=False, goal="browse")
        
    # Index risky run
    memory.record_run("risky_run_99", risky_vec, friction_score=0.85, is_regression=True, goal="checkout loop")
    
    # Query with query vector close to risky_vec
    query_vec = risky_vec + np.random.normal(0, 0.05, 64).astype(np.float32)
    results = memory.query_risky_trajectories(query_vec, top_k=3)
    
    assert len(results) > 0
    top_match = results[0]
    assert top_match["run_id"] == "risky_run_99"
    assert top_match["is_regression"] is True
