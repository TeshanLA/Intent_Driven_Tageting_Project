export type Article = {
  slug: string;
  title: string;
  category: string;
  excerpt: string;
  body: string;
};

export type Ad = {
  ad_id: string;
  title: string;
  description: string;
  category: string;
  type: string;
  target_url: string;
  cta: string;
  debug?: Record<string, unknown>;
};

export type DashboardMetric = {
  label: string;
  value: number;
};

export type DashboardSummary = {
  total_article_views: number;
  total_ad_impressions: number;
  total_ad_clicks: number;
  ctr: number;
  top_viewed_articles: DashboardMetric[];
  top_served_ads: DashboardMetric[];
  top_categories: DashboardMetric[];
  inference_mode: string;
};
