from fastapi import APIRouter, HTTPException, status
from slugify import slugify

from ai_news_db.repositories import TopicRepository
from ai_news_db.schemas import TopicCreate, TopicRead, TopicUpdate
from app.dependencies import AuthDep, SessionDep

router = APIRouter(tags=["topics"])


@router.get("", response_model=list[TopicRead])
async def list_topics(session: SessionDep, _: AuthDep):
    repo = TopicRepository(session)
    return await repo.list()


@router.get("/active", response_model=list[TopicRead])
async def list_active_topics(session: SessionDep, _: AuthDep):
    repo = TopicRepository(session)
    return await repo.list_active()


@router.get("/{topic_id}", response_model=TopicRead)
async def get_topic(topic_id: int, session: SessionDep, _: AuthDep):
    repo = TopicRepository(session)
    topic = await repo.get(topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
    return topic


@router.post("", response_model=TopicRead, status_code=status.HTTP_201_CREATED)
async def create_topic(body: TopicCreate, session: SessionDep, _: AuthDep):
    repo = TopicRepository(session)
    slug = slugify(body.name)
    existing = await repo.get_by_slug(slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Topic with slug '{slug}' already exists",
        )
    return await repo.create(name=body.name, slug=slug, description=body.description, is_active=body.is_active)


@router.put("/{topic_id}", response_model=TopicRead)
async def update_topic(topic_id: int, body: TopicUpdate, session: SessionDep, _: AuthDep):
    repo = TopicRepository(session)
    topic = await repo.get(topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
    updates = body.model_dump(exclude_unset=True)
    if "name" in updates:
        updates["slug"] = slugify(updates["name"])
    return await repo.update(topic, **updates)


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(topic_id: int, session: SessionDep, _: AuthDep):
    repo = TopicRepository(session)
    topic = await repo.get(topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
    await repo.delete(topic)
