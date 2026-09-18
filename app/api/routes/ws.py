from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.api.routes.runs import ws_subscribers
from app.core.logger import logger

router = APIRouter(tags=["websockets"])

async def _ws_handler(websocket: WebSocket, run_id: str):
    """Shared handler for both WebSocket route variants."""
    await websocket.accept()
    logger.info(f"WebSocket client connected to live feed for run {run_id}")

    if run_id not in ws_subscribers:
        ws_subscribers[run_id] = []
    ws_subscribers[run_id].append(websocket)

    try:
        while True:
            # Keep alive — receive any client ping/message
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected from run {run_id}")
    finally:
        if run_id in ws_subscribers and websocket in ws_subscribers[run_id]:
            ws_subscribers[run_id].remove(websocket)


@router.websocket("/ws/runs/{run_id}")
async def websocket_run_stream_plural(websocket: WebSocket, run_id: str):
    """WS /ws/runs/{run_id} — backend canonical route"""
    await _ws_handler(websocket, run_id)


@router.websocket("/ws/run/{run_id}")
async def websocket_run_stream_singular(websocket: WebSocket, run_id: str):
    """WS /ws/run/{run_id} — frontend contract alias"""
    await _ws_handler(websocket, run_id)
