from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.event import Event
from app.models.session_summary import SessionSummary

settings = get_settings()


def get_session_expiry_cutoff() -> datetime:
    return datetime.utcnow() - timedelta(minutes=settings.session_expiry_minutes)


def purge_expired_sessions(db: Session) -> None:
    cutoff = get_session_expiry_cutoff()

    db.query(Event).filter(Event.created_at < cutoff).delete(synchronize_session=False)
    db.query(SessionSummary).filter(SessionSummary.updated_at < cutoff).delete(synchronize_session=False)
    db.commit()
