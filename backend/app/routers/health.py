from fastapi import APIRouter

from app.services.inference import inference_service

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    return {"status": "ok", "inference_mode": inference_service.mode}
