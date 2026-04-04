from difflib import SequenceMatcher
from typing import Any

from app.services.inference import STAGE2_FEATURE_COLUMNS


def _safe_ratio(value: float) -> float:
    return round(max(0.0, min(value, 1.0)), 4)


def compute_text_similarity(article_text: str, ad_text: str) -> float:
    return _safe_ratio(SequenceMatcher(None, article_text[:500], ad_text[:250]).ratio())


def compute_category_match(page_category: str, predicted_category: str, ad_category: str) -> float:
    return 1.0 if ad_category in {page_category, predicted_category} else 0.0


def compute_behaviour_score(session_features: dict[str, Any]) -> float:
    engagement_score = float(session_features["engagement_score"])
    same_category_views = min(float(session_features["same_category_views"]) / 3.0, 1.0)
    return _safe_ratio(engagement_score * 0.6 + same_category_views * 0.4)


def build_candidate_features(
    *,
    article_category: str,
    article_text: str,
    predicted_category: str,
    stage1_confidence: float,
    session_features: dict[str, Any],
    ad: dict[str, Any],
) -> dict[str, Any]:
    """
    Keep this feature contract explicit so it can be matched directly to notebook training logic.
    """
    clean_article_text = article_text.lower().strip()
    ad_text = str(ad.get("raw_ad_text") or f"{ad.get('title', '')} {ad.get('description', '')}").strip().lower()

    features = {
        "stage1_confidence": round(float(stage1_confidence), 4),
        "category_match": compute_category_match(article_category, predicted_category, str(ad.get("category", ""))),
        "text_similarity": compute_text_similarity(clean_article_text, ad_text),
        "behaviour_score": compute_behaviour_score(session_features),
        "session_page_count": int(session_features["session_page_count"]),
        "same_category_views": int(session_features["same_category_views"]),
        "dwell_time_seconds": round(float(session_features["dwell_time_seconds"]), 4),
        "scroll_depth_ratio": _safe_ratio(float(session_features["avg_scroll_depth_ratio"])),
        "engagement_score": _safe_ratio(float(session_features["engagement_score"])),
        "ad_type_targeted": 1.0 if str(ad.get("type", "")).lower() == "targeted" else 0.0,
    }

    return {column: features[column] for column in STAGE2_FEATURE_COLUMNS}
