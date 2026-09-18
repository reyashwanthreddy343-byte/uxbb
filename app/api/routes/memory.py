from fastapi import APIRouter
from app.schemas.run import FailureMemoryStats
from app.engine.failure_memory import failure_memory
from typing import Dict, Any

router = APIRouter(prefix="/memory", tags=["memory"])

@router.get("/stats", response_model=FailureMemoryStats)
async def get_memory_stats():
    """
    GET /api/memory/stats
    Returns vector memory stats and detection speed improvement curve.
    """
    stats = failure_memory.get_memory_stats()
    return FailureMemoryStats(
        runs_seen=stats["runs_seen"],
        detection_speed_curve=stats["detection_speed_curve"],
        recall_accuracy=stats["recall_accuracy"]
    )
