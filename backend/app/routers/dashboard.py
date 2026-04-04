from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.article import Article
from app.models.event import Event
from app.schemas.dashboard import DashboardSummary, MetricItem
from app.services.inference import inference_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_article_views = db.query(func.count(Event.id)).filter(Event.event_type == "page_view").scalar() or 0
    total_ad_impressions = db.query(func.count(Event.id)).filter(Event.event_type == "ad_impression").scalar() or 0
    total_ad_clicks = db.query(func.count(Event.id)).filter(Event.event_type == "ad_click").scalar() or 0
    ctr = round((total_ad_clicks / total_ad_impressions) * 100, 2) if total_ad_impressions else 0.0

    top_articles_rows = (
        db.query(Article.title, func.count(Event.id))
        .join(Article, Article.slug == Event.article_slug)
        .filter(Event.event_type == "page_view", Event.article_slug.isnot(None))
        .group_by(Article.title)
        .order_by(func.count(Event.id).desc())
        .limit(5)
        .all()
    )
    top_ads_rows = (
        db.query(Event.ad_id, func.count(Event.id))
        .filter(Event.event_type == "ad_impression", Event.ad_id.isnot(None))
        .group_by(Event.ad_id)
        .order_by(func.count(Event.id).desc())
        .limit(5)
        .all()
    )
    top_categories_rows = (
        db.query(Event.article_category, func.count(Event.id))
        .filter(Event.event_type == "page_view", Event.article_category.isnot(None))
        .group_by(Event.article_category)
        .order_by(func.count(Event.id).desc())
        .limit(5)
        .all()
    )

    return DashboardSummary(
        total_article_views=total_article_views,
        total_ad_impressions=total_ad_impressions,
        total_ad_clicks=total_ad_clicks,
        ctr=ctr,
        top_viewed_articles=[MetricItem(label=row[0], value=row[1]) for row in top_articles_rows],
        top_served_ads=[MetricItem(label=row[0], value=row[1]) for row in top_ads_rows],
        top_categories=[MetricItem(label=row[0], value=row[1]) for row in top_categories_rows],
        inference_mode=inference_service.mode,
    )
