import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ai_news_db.repositories import PipelineRunRepository
from app.database import AsyncSessionLocal

router = APIRouter(tags=["websocket"])

POLL_INTERVAL = 2  # seconds


@router.websocket("/ws/pipeline/{run_id}")
async def pipeline_status(websocket: WebSocket, run_id: int):
    """Stream pipeline run status updates until the run reaches a terminal state."""
    await websocket.accept()
    try:
        while True:
            async with AsyncSessionLocal() as session:
                repo = PipelineRunRepository(session)
                run = await repo.get(run_id)

            if run is None:
                await websocket.send_text(json.dumps({"error": "Run not found"}))
                break

            payload = {
                "run_id": run.id,
                "status": run.status.value,
                "celery_task_id": run.celery_task_id,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
                "error_message": run.error_message,
            }
            await websocket.send_text(json.dumps(payload))

            if run.status.value in ("success", "failed"):
                break

            await asyncio.sleep(POLL_INTERVAL)

    except WebSocketDisconnect:
        pass
