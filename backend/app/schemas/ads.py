from typing import Any

from pydantic import BaseModel, Field


class AdRequestPayload(BaseModel):
    session_id: str
    article_slug: str
    article_title: str | None = None
    article_category: str | None = None
    article_text: str


class AdClickPayload(BaseModel):
    session_id: str
    ad_id: str
    article_slug: str | None = None
    article_category: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AdResponse(BaseModel):
    ad_id: str
    title: str
    description: str
    category: str
    type: str
    target_url: str
    cta: str
    debug: dict[str, Any] = Field(default_factory=dict)
