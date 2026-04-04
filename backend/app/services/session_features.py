from sqlalchemy.orm import Session

from app.models.session_summary import SessionSummary
from app.schemas.event import EventCreate


def _safe_float(value: float | int | None) -> float:
    return float(value) if value is not None else 0.0


def update_session_summary_from_event(db: Session, payload: EventCreate) -> SessionSummary:
    summary = db.query(SessionSummary).filter(SessionSummary.session_id == payload.session_id).first()
    if not summary:
        summary = SessionSummary(session_id=payload.session_id)
        db.add(summary)
        db.flush()

    if payload.event_type == "page_view":
        summary.page_count += 1
        if payload.article_category and payload.article_category == summary.last_article_category:
            summary.same_category_views += 1
        elif payload.article_category:
            summary.same_category_views = 1
        summary.last_article_category = payload.article_category

    dwell_time = _safe_float(payload.metadata.get("dwell_time_seconds"))
    scroll_depth = _safe_float(payload.metadata.get("scroll_depth_ratio"))
    completion_ratio = _safe_float(payload.metadata.get("estimated_completion_ratio"))

    if dwell_time:
        summary.total_dwell_time_seconds += dwell_time

    interaction_count = max(summary.page_count, 1)
    if scroll_depth:
        summary.avg_scroll_depth_ratio = ((summary.avg_scroll_depth_ratio * (interaction_count - 1)) + scroll_depth) / interaction_count
    if completion_ratio:
        summary.avg_completion_ratio = ((summary.avg_completion_ratio * (interaction_count - 1)) + completion_ratio) / interaction_count

    avg_dwell = summary.total_dwell_time_seconds / max(summary.page_count, 1)
    summary.engagement_score = round(
        min(1.0, (avg_dwell / 120.0) * 0.4 + summary.avg_scroll_depth_ratio * 0.3 + summary.avg_completion_ratio * 0.3),
        4,
    )

    db.commit()
    db.refresh(summary)
    return summary


def get_session_feature_snapshot(db: Session, session_id: str) -> dict:
    summary = db.query(SessionSummary).filter(SessionSummary.session_id == session_id).first()
    if not summary:
        return {
            "session_id": session_id,
            "session_page_count": 0,
            "same_category_views": 0,
            "avg_scroll_depth_ratio": 0.0,
            "avg_completion_ratio": 0.0,
            "dwell_time_seconds": 0.0,
            "engagement_score": 0.0,
        }

    return {
        "session_id": summary.session_id,
        "session_page_count": summary.page_count,
        "same_category_views": summary.same_category_views,
        "avg_scroll_depth_ratio": round(summary.avg_scroll_depth_ratio, 4),
        "avg_completion_ratio": round(summary.avg_completion_ratio, 4),
        "dwell_time_seconds": round(summary.total_dwell_time_seconds / max(summary.page_count, 1), 2),
        "engagement_score": round(summary.engagement_score, 4),
    }
