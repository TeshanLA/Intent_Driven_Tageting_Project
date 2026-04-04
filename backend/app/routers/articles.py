from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.article import Article
from app.schemas.article import ArticleResponse

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=list[ArticleResponse])
def list_articles(db: Session = Depends(get_db)):
    return db.query(Article).order_by(Article.category.asc(), Article.title.asc()).all()


@router.get("/{slug}", response_model=ArticleResponse)
def get_article(slug: str, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.slug == slug).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article
