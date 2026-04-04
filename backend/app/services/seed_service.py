import json

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models.article import Article

settings = get_settings()


def seed_demo_content():
    db: Session = SessionLocal()
    try:
        if db.query(Article).count() > 0:
            return

        articles_path = settings.resolve_path(settings.articles_json_path)
        with articles_path.open("r", encoding="utf-8") as file:
            items = json.load(file)

        for item in items:
            db.add(Article(**item))

        db.commit()
    finally:
        db.close()
