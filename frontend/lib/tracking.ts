import { postAdClick, postEvent } from "./api";

type TrackEventInput = {
  sessionId: string;
  eventType?: string;
  articleSlug?: string;
  articleCategory?: string;
  adId?: string;
  metadata?: Record<string, unknown>;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

function buildEventPayload(input: TrackEventInput) {
  return {
    session_id: input.sessionId,
    event_type: input.eventType,
    article_slug: input.articleSlug,
    article_category: input.articleCategory,
    ad_id: input.adId,
    metadata: input.metadata || {}
  };
}

export async function trackEvent(input: TrackEventInput) {
  return postEvent(buildEventPayload(input));
}

export async function trackAdClick(input: TrackEventInput) {
  return postAdClick({
    session_id: input.sessionId,
    ad_id: input.adId,
    article_slug: input.articleSlug,
    article_category: input.articleCategory,
    metadata: input.metadata || {}
  });
}

export function sendTrackingBeacon(input: TrackEventInput) {
  if (typeof navigator === "undefined" || typeof navigator.sendBeacon !== "function") {
    return false;
  }

  const payload = JSON.stringify(buildEventPayload(input));
  return navigator.sendBeacon(`${API_BASE_URL}/events`, new Blob([payload], { type: "application/json" }));
}
