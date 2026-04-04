from pydantic import BaseModel


class MetricItem(BaseModel):
    label: str
    value: int | float


class DashboardSummary(BaseModel):
    total_article_views: int
    total_ad_impressions: int
    total_ad_clicks: int
    ctr: float
    top_viewed_articles: list[MetricItem]
    top_served_ads: list[MetricItem]
    top_categories: list[MetricItem]
    inference_mode: str
