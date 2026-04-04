from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.event import Event
from app.schemas.event import EventCreate, EventResponse
from app.services.session_features import update_session_summary_from_event

router = APIRouter(tags=["events"])


@router.post("/events", response_model=EventResponse)
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    event = Event(
        session_id=payload.session_id,
        event_type=payload.event_type,
        article_slug=payload.article_slug,
        article_category=payload.article_category,
        ad_id=payload.ad_id,
        event_metadata=payload.metadata,
    )
    db.add(event)
    db.commit()
    update_session_summary_from_event(db=db, payload=payload)
    return EventResponse(success=True)
