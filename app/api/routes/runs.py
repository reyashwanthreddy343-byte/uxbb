import os
import uuid
import asyncio
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas.run import RunRequest, RunResponse
from app.schemas.findings import RunReport
from app.engine.orchestrator import orchestrator
from app.core.logger import logger

router = APIRouter(tags=["runs"])

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

# Storage for in-flight/recent screenshots: run_id -> dict(step_idx -> bytes)
run_screenshots: Dict[str, Dict[int, bytes]] = {}

@router.get("/runs/{run_id}/screenshots/{step_number}")
async def get_step_screenshot(run_id: str, step_number: int):
    """Serve real PNG screenshot for trajectory scrub/replay player."""
    from fastapi.responses import Response
    import base64
    screenshots = run_screenshots.get(run_id, {})
    if step_number in screenshots:
        return Response(content=screenshots[step_number], media_type="image/png")
    
    # Check completed runs
    if run_id in completed_runs:
        run_report = completed_runs[run_id]
        for step in run_report.steps:
            if step.step_number == step_number and step.screenshot_base64:
                try:
                    img_bytes = base64.b64decode(step.screenshot_base64)
                    return Response(content=img_bytes, media_type="image/png")
                except Exception:
                    pass

    # Return a 1x1 transparent PNG fallback if not yet generated
    transparent_png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=")
    return Response(content=transparent_png, media_type="image/png")

@router.get("/run/{run_id}/screenshots/{step_number}")
async def get_step_screenshot_singular(run_id: str, step_number: int):
    return await get_step_screenshot(run_id, step_number)

@router.post("/runs", response_model=RunResponse)
async def start_run(request: RunRequest, background_tasks: BackgroundTasks):
    """
    POST /api/runs  (and alias POST /api/run)
    Initiates an autonomous black-box UI testing session.
    """
    return await _create_run(request, background_tasks)

@router.get("/runs/{run_id}")
async def get_run_report(run_id: str):
    """GET /api/runs/{run_id}  (and alias GET /api/run/{run_id}/report)"""
    return _fetch_report(run_id)

# ─── Singular aliases: /api/run  (frontend contract) ──────────────────────────

@router.post("/run", response_model=RunResponse)
async def start_run_singular(request: RunRequest, background_tasks: BackgroundTasks):
    """POST /api/run — frontend-facing alias"""
    return await _create_run(request, background_tasks)

@router.get("/run/{run_id}/report")
async def get_run_report_singular(run_id: str):
    """GET /api/run/{run_id}/report — frontend-facing alias"""
    return _fetch_report(run_id)

@router.get("/run/{run_id}")
async def get_run_singular(run_id: str):
    """GET /api/run/{run_id} — convenience alias"""
    return _fetch_report(run_id)

# ─── Shared implementation ────────────────────────────────────────────────────

async def _create_run(request: RunRequest, background_tasks: BackgroundTasks) -> RunResponse:
    run_id = f"run_{uuid.uuid4().hex[:8]}"
    target_url = request.resolved_target_url
    logger.info(f"Received request to start test run {run_id} for {target_url}")

    async def execute_run():
        try:
            async def ws_callback(event):
                # Save screenshot bytes if present for the screenshot serving route
                if event.get("type") == "step":
                    step_data = event.get("data", {})
                    step_num = step_data.get("step_number") or step_data.get("index")
                    b64 = step_data.get("screenshot_base64")
                    if b64 and step_num:
                        import base64
                        try:
                            if run_id not in run_screenshots:
                                run_screenshots[run_id] = {}
                            run_screenshots[run_id][step_num] = base64.b64decode(b64)
                        except Exception:
                            pass
                await broadcast_event(run_id, event)

            report = await orchestrator.run_test_session(
                run_id=run_id,
                goal=request.goal,
                target_url=target_url,
                platform=request.platform,
                event_callback=ws_callback
            )
            completed_runs[run_id] = report
            logger.info(f"Run {run_id} completed successfully.")
        except Exception as e:
            logger.error(f"Run {run_id} encountered execution error: {e}", exc_info=True)

    background_tasks.add_task(execute_run)
    return RunResponse(run_id=run_id)

def _fetch_report(run_id: str):
    if run_id in completed_runs:
        return completed_runs[run_id]
    raise HTTPException(status_code=404, detail=f"Run {run_id} not found or still processing.")
