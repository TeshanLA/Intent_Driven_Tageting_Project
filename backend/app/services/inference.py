import json
import logging
import re
from pathlib import Path
from typing import Any

import joblib

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

STAGE2_FEATURE_COLUMNS = [
    "stage1_confidence",
    "category_match",
    "text_similarity",
    "behaviour_score",
    "session_page_count",
    "same_category_views",
    "dwell_time_seconds",
    "scroll_depth_ratio",
    "engagement_score",
    "ad_type_targeted",
]


class InferenceService:
    def __init__(self) -> None:
        self.model_dir = settings.resolve_path(settings.model_dir)
        self.mode = "mock"
        self.stage1_vectorizer = None
        self.stage1_model = None
        self.stage2_model = None
        self.category_mapping: dict[str, str] = {}
        self.artifact_status: dict[str, dict[str, Any]] = {}

    def load_artifacts(self) -> None:
        self.model_dir.mkdir(parents=True, exist_ok=True)

        vectorizer_path = self.model_dir / "stage1_vectorizer.joblib"
        stage1_path = self.model_dir / "stage1_model.joblib"
        stage2_path = self.model_dir / "stage2_model.joblib"
        mapping_path = self.model_dir / "category_mapping.json"

        self.stage1_vectorizer = None
        self.stage1_model = None
        self.stage2_model = None
        self.category_mapping = {}

        self._load_stage1(vectorizer_path=vectorizer_path, stage1_path=stage1_path, mapping_path=mapping_path)
        self._load_stage2(stage2_path=stage2_path)

        if self.stage1_vectorizer is not None and self.stage1_model is not None and self.stage2_model is not None:
            self.mode = "real_model"
        else:
            self.mode = "mock"

        logger.info("Inference mode resolved to %s", self.mode)

    def preprocess_article_text(self, article_text: str) -> dict[str, Any]:
        normalized = re.sub(r"\s+", " ", article_text.strip())
        lowered = normalized.lower()
        tokens = re.findall(r"\b\w+\b", lowered)

        return {
            "raw_text": article_text,
            "clean_text": normalized,
            "lower_text": lowered,
            "token_count": len(tokens),
            "char_count": len(normalized),
        }

    def run_stage1(self, article_text: str, provided_category: str | None = None) -> dict[str, Any]:
        preprocessed = self.preprocess_article_text(article_text)

        if self.stage1_vectorizer is not None and self.stage1_model is not None:
            try:
                vectorized = self.stage1_vectorizer.transform([preprocessed["clean_text"]])
                raw_prediction = self.stage1_model.predict(vectorized)[0]
                predicted_category = str(self.category_mapping.get(str(raw_prediction), raw_prediction))
                confidence = 0.8
                if hasattr(self.stage1_model, "predict_proba"):
                    probabilities = self.stage1_model.predict_proba(vectorized)[0]
                    confidence = float(max(probabilities))

                return {
                    "predicted_category": predicted_category,
                    "confidence": round(confidence, 4),
                    "mode": "real_model",
                    "preprocessed": preprocessed,
                }
            except Exception as exc:
                logger.warning("Stage 1 inference failed. Falling back to mock logic: %s", exc)

        predicted_category, confidence = self._mock_predict_category(
            article_text=preprocessed["lower_text"],
            provided_category=provided_category,
        )
        return {
            "predicted_category": predicted_category,
            "confidence": round(confidence, 4),
            "mode": "mock",
            "preprocessed": preprocessed,
        }

    def run_stage2(self, feature_vector: dict[str, Any]) -> dict[str, Any]:
        if self.stage2_model is not None:
            try:
                ordered = [feature_vector[column] for column in STAGE2_FEATURE_COLUMNS]
                score = float(self.stage2_model.predict([ordered])[0])
                return {"score": round(score, 4), "mode": "real_model", "ordered_features": ordered}
            except Exception as exc:
                logger.warning("Stage 2 ranking failed. Falling back to heuristic reranking: %s", exc)

        heuristic_score = self.heuristic_stage2_score(feature_vector)
        return {
            "score": heuristic_score,
            "mode": "heuristic_fallback",
            "ordered_features": [feature_vector[column] for column in STAGE2_FEATURE_COLUMNS],
        }

    def heuristic_stage2_score(self, feature_vector: dict[str, Any]) -> float:
        return round(
            feature_vector["category_match"] * 0.35
            + feature_vector["text_similarity"] * 0.1
            + feature_vector["behaviour_score"] * 0.2
            + feature_vector["stage1_confidence"] * 0.15
            + feature_vector["engagement_score"] * 0.1
            + feature_vector["ad_type_targeted"] * 0.1,
            4,
        )

    def get_status_summary(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "model_dir": str(self.model_dir),
            "feature_columns": STAGE2_FEATURE_COLUMNS,
            "artifacts": self.artifact_status,
        }

    def _load_stage1(self, *, vectorizer_path: Path, stage1_path: Path, mapping_path: Path) -> None:
        stage1_loaded = False
        vectorizer_loaded = False

        if vectorizer_path.exists():
            try:
                self.stage1_vectorizer = joblib.load(vectorizer_path)
                vectorizer_loaded = True
                logger.info("Loaded stage1 vectorizer from %s", vectorizer_path)
            except Exception as exc:
                logger.warning("Failed to load stage1 vectorizer from %s: %s", vectorizer_path, exc)
        else:
            logger.info("Stage1 vectorizer missing at %s", vectorizer_path)

        if stage1_path.exists():
            try:
                self.stage1_model = joblib.load(stage1_path)
                stage1_loaded = True
                logger.info("Loaded stage1 model from %s", stage1_path)
            except Exception as exc:
                logger.warning("Failed to load stage1 model from %s: %s", stage1_path, exc)
        else:
            logger.info("Stage1 model missing at %s", stage1_path)

        mapping_loaded = False
        if mapping_path.exists():
            try:
                self.category_mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
                mapping_loaded = True
                logger.info("Loaded category mapping from %s", mapping_path)
            except Exception as exc:
                logger.warning("Failed to load category mapping from %s: %s", mapping_path, exc)
        else:
            logger.info("Category mapping missing at %s", mapping_path)

        self.artifact_status["stage1_vectorizer"] = self._artifact_entry(vectorizer_path, vectorizer_loaded)
        self.artifact_status["stage1_model"] = self._artifact_entry(stage1_path, stage1_loaded)
        self.artifact_status["category_mapping"] = self._artifact_entry(mapping_path, mapping_loaded)

    def _load_stage2(self, *, stage2_path: Path) -> None:
        stage2_loaded = False
        if stage2_path.exists():
            try:
                self.stage2_model = joblib.load(stage2_path)
                stage2_loaded = True
                logger.info("Loaded stage2 model from %s", stage2_path)
            except Exception as exc:
                logger.warning("Failed to load stage2 model from %s: %s", stage2_path, exc)
        else:
            logger.info("Stage2 model missing at %s", stage2_path)

        self.artifact_status["stage2_model"] = self._artifact_entry(stage2_path, stage2_loaded)

    def _artifact_entry(self, path: Path, loaded: bool) -> dict[str, Any]:
        return {"path": str(path), "exists": path.exists(), "loaded": loaded}

    def _mock_predict_category(self, article_text: str, provided_category: str | None = None) -> tuple[str, float]:
        if provided_category:
            return provided_category, 0.92

        text = article_text.lower()
        keyword_map = {
            "Sports": ["match", "goal", "coach", "final", "league"],
            "Business": ["market", "stock", "earnings", "revenue", "investor"],
            "Entertainment": ["streaming", "studio", "cast", "movie", "franchise"],
            "Health": ["health", "doctor", "sleep", "fitness", "walking"],
            "Travel": ["travel", "trip", "rail", "hotel", "tourism"],
            "Lifestyle": ["design", "living", "decor", "home", "style"],
            "Food": ["cooking", "chef", "recipe", "spice", "meal"],
            "General News": ["council", "official", "city", "public", "plan"],
        }
        best_category = "General News"
        best_score = 0
        for category, keywords in keyword_map.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > best_score:
                best_score = score
                best_category = category

        confidence = 0.55 + min(best_score * 0.08, 0.35)
        return best_category, round(confidence, 4)


inference_service = InferenceService()
