from sqlalchemy import Column, String, Text

from app.core.database import Base


class Article(Base):
    __tablename__ = "articles"

    slug = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False, index=True)
    excerpt = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
