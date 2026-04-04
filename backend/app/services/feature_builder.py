from difflib import SequenceMatcher


def build_candidate_features(
    *,
    article_category: str,
    article_text: str,
    predicted_category: str,
    stage1_confidence: float,
    session_features: dict,
    ad: dict,
) -> dict:
    ad_text = f"{ad.get('title', '')} {ad.get('description', '')}".strip().lower()
    page_text = article_text.lower()
    text_similarity = round(SequenceMatcher(None, page_text[:300], ad_text).ratio(), 4)
    category_match = 1.0 if ad.get("category") in {article_category, predicted_category} else 0.0
    ad_type_targeted = 1.0 if ad.get("type") == "targeted" else 0.0
    behaviour_score = round(
        min(
            1.0,
            session_features["engagement_score"] * 0.6
            + min(session_features["same_category_views"] / 3.0, 1.0) * 0.4,
        ),
        4,
    )

    return {
        "stage1_confidence": round(stage1_confidence, 4),
        "category_match": category_match,
        "text_similarity": text_similarity,
        "behaviour_score": behaviour_score,
        "session_page_count": session_features["session_page_count"],
        "same_category_views": session_features["same_category_views"],
        "dwell_time_seconds": session_features["dwell_time_seconds"],
        "scroll_depth_ratio": session_features["avg_scroll_depth_ratio"],
        "engagement_score": session_features["engagement_score"],
        "ad_type_targeted": ad_type_targeted,
    }
