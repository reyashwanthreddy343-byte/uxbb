from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.api.routes.runs import ws_subscribers
from app.core.logger import logger

router = APIRouter(tags=["websockets"])

@router.websocket("/ws/runs/{run_id}")
async def websocket_run_stream(websocket: WebSocket, run_id: str):
    """
    WS /ws/runs/{run_id}
    Streams real-time step events, annotated overlays, model findings, and done signals.
    """
    await websocket.accept()
    logger.info(f"WebSocket client connected to live feed for run {run_id}")
    
    if run_id not in ws_subscribers:
        ws_subscribers[run_id] = []
    ws_subscribers[run_id].append(websocket)
    
    try:
        while True:
            # Keep alive and receive any client ping
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected from run {run_id}")
    finally:
        if run_id in ws_subscribers and websocket in ws_subscribers[run_id]:
            ws_subscribers[run_id].remove(websocket)
