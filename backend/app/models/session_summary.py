from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from app.core.database import Base


class SessionSummary(Base):
    __tablename__ = "session_summaries"

    session_id = Column(String, primary_key=True, index=True)
    page_count = Column(Integer, nullable=False, default=0)
    total_dwell_time_seconds = Column(Float, nullable=False, default=0.0)
    avg_scroll_depth_ratio = Column(Float, nullable=False, default=0.0)
    avg_completion_ratio = Column(Float, nullable=False, default=0.0)
    engagement_score = Column(Float, nullable=False, default=0.0)
    last_article_category = Column(String, nullable=True)
    same_category_views = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
