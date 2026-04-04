import csv
import logging
from functools import lru_cache
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.schemas.ads import AdRequestPayload
from app.services.feature_builder import build_candidate_features
from app.services.inference import inference_service
from app.services.session_features import get_session_feature_snapshot

logger = logging.getLogger(__name__)
settings = get_settings()

_ads_inventory_status: dict[str, Any] = {}


def initialize_ads_inventory() -> None:
    load_ads_inventory.cache_clear()
    ads = load_ads_inventory()
    logger.info("Ads inventory loaded with %s candidate ads", len(ads))


@lru_cache
def load_ads_inventory() -> list[dict[str, Any]]:
    global _ads_inventory_status

    ads_path = settings.resolve_path(settings.ads_csv_path)
    if not ads_path.exists():
        _ads_inventory_status = {
            "path": str(ads_path),
            "exists": False,
            "loaded": False,
            "count": 1,
            "mode": "fallback_inventory",
        }
        logger.warning("Ads inventory missing at %s. Using built-in fallback inventory.", ads_path)
        return [_fallback_ad()]

    try:
        with ads_path.open("r", encoding="utf-8") as file:
            raw_ads = list(csv.DictReader(file))
        ads = [_normalize_ad_record(row) for row in raw_ads]
        if not ads:
            raise ValueError("ads inventory is empty")

        _ads_inventory_status = {
            "path": str(ads_path),
            "exists": True,
            "loaded": True,
            "count": len(ads),
            "mode": "csv_inventory",
        }
        logger.info("Loaded ads inventory from %s", ads_path)
        return ads
    except Exception as exc:
        _ads_inventory_status = {
            "path": str(ads_path),
            "exists": ads_path.exists(),
            "loaded": False,
            "count": 1,
            "mode": "fallback_inventory",
            "error": str(exc),
        }
        logger.warning("Failed to load ads inventory from %s: %s. Using fallback inventory.", ads_path, exc)
        return [_fallback_ad()]


def get_ads_inventory_status() -> dict[str, Any]:
    if not _ads_inventory_status:
        load_ads_inventory()
    return _ads_inventory_status


def run_ad_selection_pipeline(db: Session, payload: AdRequestPayload) -> dict[str, Any]:
    session_features = get_session_feature_snapshot(db=db, session_id=payload.session_id)
    stage1_result = inference_service.run_stage1(
        article_text=payload.article_text,
        provided_category=payload.article_category,
    )
    target_category = payload.article_category or stage1_result["predicted_category"]

    ads = load_ads_inventory()
    preferred_ads = [
        ad
        for ad in ads
        if ad.get("category") in {target_category, stage1_result["predicted_category"]} or ad.get("type") == "generic"
    ]
    candidate_ads = preferred_ads or ads

    ranked_candidates: list[dict[str, Any]] = []
    for ad in candidate_ads:
        candidate_features = build_candidate_features(
            article_category=target_category,
            article_text=stage1_result["preprocessed"]["clean_text"],
            predicted_category=stage1_result["predicted_category"],
            stage1_confidence=stage1_result["confidence"],
            session_features=session_features,
            ad=ad,
        )
        stage2_result = inference_service.run_stage2(candidate_features)
        ranked_candidates.append(
            {
                "ad": ad,
                "features": candidate_features,
                "score": stage2_result["score"],
                "ranking_mode": stage2_result["mode"],
                "ordered_features": stage2_result["ordered_features"],
            }
        )

    ranked_candidates.sort(key=lambda item: item["score"], reverse=True)

    if not ranked_candidates:
        return {
            "selected_ad": _fallback_ad(),
            "session_features": session_features,
            "stage1": stage1_result,
            "ranking_mode": "fallback_inventory",
            "ranked_candidates": [],
        }

    return {
        "selected_ad": ranked_candidates[0]["ad"],
        "selected_candidate": ranked_candidates[0],
        "session_features": session_features,
        "stage1": stage1_result,
        "ranking_mode": ranked_candidates[0]["ranking_mode"],
        "ranked_candidates": ranked_candidates,
    }


def select_best_ad(db: Session, payload: AdRequestPayload) -> dict[str, Any]:
    pipeline = run_ad_selection_pipeline(db=db, payload=payload)
    selected_ad = pipeline["selected_ad"]
    selected_candidate = pipeline.get("selected_candidate")

    debug = {
        "predicted_category": pipeline["stage1"]["predicted_category"],
        "stage1_confidence": pipeline["stage1"]["confidence"],
        "stage1_mode": pipeline["stage1"]["mode"],
        "ranking_mode": pipeline["ranking_mode"],
        "preprocessing_summary": {
            "token_count": pipeline["stage1"]["preprocessed"]["token_count"],
            "char_count": pipeline["stage1"]["preprocessed"]["char_count"],
        },
        "session_features": pipeline["session_features"],
        "top_feature_summary": selected_candidate["features"] if selected_candidate else {"reason": "fallback_inventory"},
        "ranking_score": selected_candidate["score"] if selected_candidate else None,
    }

    return {**selected_ad, "debug": debug}


def _fallback_ad() -> dict[str, Any]:
    return {
        "ad_id": "ad-generic-fallback",
        "title": "Prototype Sponsor",
        "description": "Fallback demo ad shown when the inventory file is missing or invalid.",
        "category": "Generic",
        "type": "generic",
        "target_url": "https://example.com/fallback",
        "cta": "Learn More",
    }


def _normalize_ad_record(row: dict[str, Any]) -> dict[str, Any]:
    if row.get("title") and row.get("description"):
        return {
            "ad_id": str(row.get("ad_id", "")).strip(),
            "title": str(row.get("title", "")).strip(),
            "description": str(row.get("description", "")).strip(),
            "category": _normalize_category(str(row.get("category", "Generic"))),
            "type": str(row.get("type", "generic")).strip().lower() or "generic",
            "target_url": str(row.get("target_url", "https://example.com/demo")).strip() or "https://example.com/demo",
            "cta": str(row.get("cta", "Learn More")).strip() or "Learn More",
            "category_confidence": _safe_float(row.get("category_confidence")),
            "raw_ad_text": str(row.get("ad_text", "")).strip(),
        }

    ad_text = str(row.get("ad_text", "")).strip()
    title, description = _split_ad_text(ad_text)
    ad_id = str(row.get("ad_id", "")).strip() or "ad-unknown"
    ad_type = str(row.get("type", "generic")).strip().lower() or "generic"
    category = _normalize_category(str(row.get("category", "Generic")))

    return {
        "ad_id": ad_id,
        "title": title,
        "description": description,
        "category": category,
        "type": ad_type,
        "target_url": f"https://example.com/ads/{ad_id.lower()}",
        "cta": "Learn More" if ad_type == "generic" else "View Offer",
        "category_confidence": _safe_float(row.get("category_confidence")),
        "raw_ad_text": ad_text,
    }


def _split_ad_text(ad_text: str) -> tuple[str, str]:
    cleaned_lines = [line.strip() for line in ad_text.splitlines() if line.strip()]
    if not cleaned_lines:
        return "Sponsored Demo Ad", "No ad copy available."

    title = " ".join(cleaned_lines[:2])[:80].strip()
    remaining = " ".join(cleaned_lines[2:]).strip()
    description = remaining[:220].strip() if remaining else title
    return title or "Sponsored Demo Ad", description or "No ad copy available."


def _normalize_category(category: str) -> str:
    normalized = category.replace("_", " ").strip()
    lowered = normalized.lower()
    if lowered in {"general news", "general"}:
        return "General News"
    return normalized or "Generic"


def _safe_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None
