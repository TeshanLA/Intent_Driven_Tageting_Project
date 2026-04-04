from typing import Any

from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    session_id: str
    event_type: str
    article_slug: str | None = None
    article_category: str | None = None
    ad_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EventResponse(BaseModel):
    success: bool
