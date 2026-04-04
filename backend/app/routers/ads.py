from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.event import Event
from app.schemas.ads import AdClickPayload, AdRequestPayload, AdResponse
from app.services.ad_selector import select_best_ad

router = APIRouter(tags=["ads"])


@router.post("/ad/request", response_model=AdResponse)
def request_ad(payload: AdRequestPayload, db: Session = Depends(get_db)):
    selection = select_best_ad(db=db, payload=payload)
    return AdResponse(**selection)


@router.post("/ad/click")
def log_ad_click(payload: AdClickPayload, db: Session = Depends(get_db)):
    event = Event(
        session_id=payload.session_id,
        event_type="ad_click",
        article_slug=payload.article_slug,
        article_category=payload.article_category,
        ad_id=payload.ad_id,
        event_metadata=payload.metadata,
    )
    db.add(event)
    db.commit()
    return {"success": True}
