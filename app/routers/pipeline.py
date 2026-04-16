from fastapi import APIRouter, HTTPException, Query, status

from ai_news_db.repositories import PipelineRunRepository, TopicRepository
from ai_news_db.schemas import PipelineRunCreate, PipelineRunRead
from app.celery_app import celery_app
from app.dependencies import AuthDep, SessionDep

router = APIRouter(tags=["pipeline"])


@router.post("/trigger", response_model=PipelineRunRead, status_code=status.HTTP_202_ACCEPTED)
async def trigger_pipeline(body: PipelineRunCreate, session: SessionDep, _: AuthDep):
    """Create a pipeline run record and dispatch a Celery task."""
    topic_repo = TopicRepository(session)
    topic = await topic_repo.get(body.topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
    if not topic.is_active:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Topic is inactive",
        )

    run_repo = PipelineRunRepository(session)
    run = await run_repo.create(topic_id=body.topic_id)

    # Dispatch to Celery — the scheduler/worker service consumes this task
    task = celery_app.send_task(
        "pipeline.run",
        kwargs={"run_id": run.id, "topic_id": topic.id, "topic_slug": topic.slug},
        queue="pipeline",
    )
    run = await run_repo.mark_running(run, celery_task_id=task.id)
    return run


@router.get("/runs", response_model=list[PipelineRunRead])
async def list_runs(
    session: SessionDep,
    _: AuthDep,
    topic_id: int | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
):
    run_repo = PipelineRunRepository(session)
    if topic_id is not None:
        return await run_repo.list_by_topic(topic_id, limit=limit)
    return await run_repo.list(limit=limit) if hasattr(run_repo, "list") else []


@router.get("/runs/{run_id}", response_model=PipelineRunRead)
async def get_run(run_id: int, session: SessionDep, _: AuthDep):
    run_repo = PipelineRunRepository(session)
    run = await run_repo.get(run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline run not found")
    return run
