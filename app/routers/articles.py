from fastapi import APIRouter, HTTPException, Query, status

from ai_news_db.repositories import ArticleRepository
from ai_news_db.schemas import ArticleRead
from app.dependencies import SessionDep

router = APIRouter(tags=["articles"])


@router.get("", response_model=list[ArticleRead])
async def list_articles(
    session: SessionDep,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    repo = ArticleRepository(session)
    return await repo.list_published(limit=limit, offset=offset)


@router.get("/{slug}", response_model=ArticleRead)
async def get_article(slug: str, session: SessionDep):
    repo = ArticleRepository(session)
    article = await repo.get_by_slug(slug)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return article
