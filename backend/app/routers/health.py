from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.ads import AdRequestPayload
from app.services.ad_selector import get_ads_inventory_status, run_ad_selection_pipeline
from app.services.inference import inference_service

router = APIRouter(tags=["health", "debug"])


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "inference_mode": inference_service.mode,
        "artifacts": inference_service.get_status_summary()["artifacts"],
        "ads_inventory": get_ads_inventory_status(),
    }


@router.get("/debug/inference/status")
def inference_status():
    return {
        "inference": inference_service.get_status_summary(),
        "ads_inventory": get_ads_inventory_status(),
    }


@router.post("/debug/inference/inspect")
def inspect_inference(payload: AdRequestPayload, db: Session = Depends(get_db)):
    pipeline = run_ad_selection_pipeline(db=db, payload=payload)
    preview_candidates = [
        {
            "ad_id": item["ad"]["ad_id"],
            "title": item["ad"]["title"],
            "score": item["score"],
            "ranking_mode": item["ranking_mode"],
            "features": item["features"],
        }
        for item in pipeline.get("ranked_candidates", [])[:5]
    ]

    return {
        "mode": inference_service.mode,
        "selected_ad": pipeline["selected_ad"],
        "stage1": pipeline["stage1"],
        "session_features": pipeline["session_features"],
        "ranking_mode": pipeline["ranking_mode"],
        "candidate_count": len(pipeline.get("ranked_candidates", [])),
        "top_candidates": preview_candidates,
    }
