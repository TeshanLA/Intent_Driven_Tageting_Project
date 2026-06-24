import type { Ad, Article, DashboardSummary } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers || {})
      }
    });
  } catch (error) {
    throw new Error(`Unable to reach backend at ${API_BASE_URL}${path}`, {
      cause: error
    });
  }

  if (!response.ok) {
    throw new Error(`API request failed for ${path}`);
  }

  return response.json() as Promise<T>;
}

export function fetchArticles() {
  return apiFetch<Article[]>("/articles");
}

export function fetchArticle(slug: string) {
  return apiFetch<Article>(`/articles/${slug}`);
}

export function fetchDashboardSummaryForSession(sessionId: string) {
  return apiFetch<DashboardSummary>(`/dashboard/summary?session_id=${encodeURIComponent(sessionId)}`);
}

export function getEmptyDashboardSummary(): DashboardSummary {
  return {
    total_article_views: 0,
    total_ad_impressions: 0,
    total_ad_clicks: 0,
    ctr: 0,
    top_viewed_articles: [],
    top_served_ads: [],
    top_categories: [],
    inference_mode: "backend_unavailable"
  };
}

export function fetchAd(payload: Record<string, unknown>) {
  return apiFetch<Ad>("/ad/request", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function postEvent(payload: Record<string, unknown>) {
  return apiFetch<{ success: boolean }>("/events", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function postAdClick(payload: Record<string, unknown>) {
  return apiFetch<{ success: boolean }>("/ad/click", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}
