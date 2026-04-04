from sqlalchemy import JSON, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.core.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False, index=True)
    article_slug = Column(String, nullable=True, index=True)
    article_category = Column(String, nullable=True, index=True)
    ad_id = Column(String, nullable=True, index=True)
    event_metadata = Column("metadata", JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
