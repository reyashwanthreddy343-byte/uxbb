import os
import uuid
import asyncio
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas.run import RunRequest, RunResponse
from app.schemas.findings import RunReport
from app.engine.orchestrator import orchestrator
from app.core.logger import logger

router = APIRouter(prefix="/runs", tags=["runs"])

# In-memory storage of completed runs
completed_runs: Dict[str, RunReport] = {}
active_tasks: Dict[str, asyncio.Task] = {}

# Broadcast callback registry for WebSocket integration
ws_subscribers: Dict[str, List[Any]] = {}

async def broadcast_event(run_id: str, event: Dict[str, Any]):
    subscribers = ws_subscribers.get(run_id, [])
    for ws in subscribers:
        try:
            await ws.send_json(event)
        except Exception as e:
            logger.warning(f"Error sending event to WS subscriber: {e}")

@router.post("", response_model=RunResponse)
async def start_run(request: RunRequest, background_tasks: BackgroundTasks):
    """
    POST /api/runs
    Initiates an autonomous black-box UI testing session.
    """
    run_id = f"run_{uuid.uuid4().hex[:8]}"
    logger.info(f"Received request to start test run {run_id} for {request.target_url}")
    
    async def execute_run():
        try:
            async def ws_callback(event):
                await broadcast_event(run_id, event)
                
            report = await orchestrator.run_test_session(
                run_id=run_id,
                goal=request.goal,
                target_url=request.target_url,
                platform=request.platform,
                event_callback=ws_callback
            )
            completed_runs[run_id] = report
            logger.info(f"Run {run_id} completed successfully.")
        except Exception as e:
            logger.error(f"Run {run_id} encountered execution error: {e}", exc_info=True)
            
    background_tasks.add_task(execute_run)
    return RunResponse(run_id=run_id)

@router.get("/{run_id}", response_model=RunReport)
async def get_run_report(run_id: str):
    """
    GET /api/runs/{run_id}
    Returns the full diagnostic report for the specified run.
    """
    if run_id in completed_runs:
        return completed_runs[run_id]
        
    # Return in-progress status if still running
    raise HTTPException(status_code=404, detail=f"Run report for {run_id} not found or still processing.")
