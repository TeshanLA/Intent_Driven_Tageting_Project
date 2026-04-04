import csv
from functools import lru_cache

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.schemas.ads import AdRequestPayload
from app.services.feature_builder import build_candidate_features
from app.services.inference import inference_service
from app.services.session_features import get_session_feature_snapshot

settings = get_settings()


@lru_cache
def load_ads_inventory() -> list[dict]:
    ads_path = settings.resolve_path(settings.ads_csv_path)
    if not ads_path.exists():
        return [
            {
                "ad_id": "ad-generic-fallback",
                "title": "Prototype Sponsor",
                "description": "Fallback demo ad shown when the inventory file is missing.",
                "category": "Generic",
                "type": "generic",
                "target_url": "https://example.com/fallback",
                "cta": "Learn More",
            }
        ]

    with ads_path.open("r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def select_best_ad(db: Session, payload: AdRequestPayload) -> dict:
    session_features = get_session_feature_snapshot(db=db, session_id=payload.session_id)
    predicted_category, stage1_confidence = inference_service.predict_category(
        article_text=payload.article_text,
        provided_category=payload.article_category,
    )
    target_category = payload.article_category or predicted_category

    ads = load_ads_inventory()
    preferred_ads = [
        ad for ad in ads if ad.get("category") in {target_category, predicted_category} or ad.get("type") == "generic"
    ]
    candidate_ads = preferred_ads or ads

    ranked_candidates: list[tuple[float, dict, dict]] = []
    for ad in candidate_ads:
        features = build_candidate_features(
            article_category=target_category,
            article_text=payload.article_text,
            predicted_category=predicted_category,
            stage1_confidence=stage1_confidence,
            session_features=session_features,
            ad=ad,
        )
        score = inference_service.score_stage2(features)
        ranked_candidates.append((score, ad, features))

    ranked_candidates.sort(key=lambda item: item[0], reverse=True)

    if not ranked_candidates:
        fallback = {
            "ad_id": "ad-generic-fallback",
            "title": "Prototype Sponsor",
            "description": "Fallback demo ad shown when ranking fails.",
            "category": "Generic",
            "type": "generic",
            "target_url": "https://example.com/fallback",
            "cta": "Learn More",
        }
        return {
            **fallback,
            "debug": {
                "predicted_category": predicted_category,
                "stage1_confidence": stage1_confidence,
                "ranking_mode": inference_service.mode,
                "top_feature_summary": {"reason": "hard_fallback"},
            },
        }

    top_score, best_ad, best_features = ranked_candidates[0]
    return {
        **best_ad,
        "debug": {
            "predicted_category": predicted_category,
            "stage1_confidence": stage1_confidence,
            "ranking_mode": inference_service.mode,
            "ranking_score": round(top_score, 4),
            "top_feature_summary": best_features,
        },
    }
