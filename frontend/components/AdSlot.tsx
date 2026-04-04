import { useEffect, useRef } from "react";

import { getSessionId } from "../lib/session";
import { trackAdClick, trackEvent } from "../lib/tracking";
import type { Ad, Article } from "../lib/types";

export function AdSlot({ ad, article }: { ad: Ad | null; article: Article }) {
  const lastTrackedAdIdRef = useRef<string | null>(null);

  useEffect(() => {
    if (!ad || lastTrackedAdIdRef.current === ad.ad_id) {
      return;
    }

    lastTrackedAdIdRef.current = ad.ad_id;
    void trackEvent({
      sessionId: getSessionId(),
      eventType: "ad_impression",
      articleSlug: article.slug,
      articleCategory: article.category,
      adId: ad.ad_id,
      metadata: {
        ranking_mode: ad.debug?.ranking_mode,
        predicted_category: ad.debug?.predicted_category
      }
    });
  }, [ad, article.category, article.slug]);

  if (!ad) {
    return (
      <aside className="ad-slot loading">
        <p className="sponsored-label">Sponsored</p>
        <p>Loading ad recommendation...</p>
      </aside>
    );
  }

  const handleClick = async () => {
    await trackAdClick({
      sessionId: getSessionId(),
      adId: ad.ad_id,
      articleSlug: article.slug,
      articleCategory: article.category,
      metadata: { target_url: ad.target_url }
    });
  };

  return (
    <aside className="ad-slot">
      <div className="ad-slot-header">
        <p className="sponsored-label">Sponsored Demo Ad</p>
        <span className="ad-type">{ad.type}</span>
      </div>
      <h2>{ad.title}</h2>
      <p>{ad.description}</p>
      <a className="ad-cta" href={ad.target_url} onClick={handleClick} rel="noreferrer" target="_blank">
        {ad.cta}
      </a>
      {ad.debug ? (
        <div className="ad-debug">
          <p>Predicted category: {String(ad.debug.predicted_category ?? "-")}</p>
          <p>Stage 1 confidence: {String(ad.debug.stage1_confidence ?? "-")}</p>
          <p>Ranking mode: {String(ad.debug.ranking_mode ?? "-")}</p>
        </div>
      ) : null}
    </aside>
  );
}
