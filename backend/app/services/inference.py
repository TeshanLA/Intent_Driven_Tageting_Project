import json
import logging

import joblib

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class InferenceService:
    def __init__(self) -> None:
        self.model_dir = settings.resolve_path(settings.model_dir)
        self.mode = "mock"
        self.stage1_vectorizer = None
        self.stage1_model = None
        self.stage2_model = None
        self.category_mapping: dict[str, str] = {}

    def load_artifacts(self) -> None:
        self.model_dir.mkdir(parents=True, exist_ok=True)
        vectorizer_path = self.model_dir / "stage1_vectorizer.joblib"
        stage1_path = self.model_dir / "stage1_model.joblib"
        stage2_path = self.model_dir / "stage2_model.joblib"
        mapping_path = self.model_dir / "category_mapping.json"

        try:
            if vectorizer_path.exists() and stage1_path.exists() and stage2_path.exists():
                self.stage1_vectorizer = joblib.load(vectorizer_path)
                self.stage1_model = joblib.load(stage1_path)
                self.stage2_model = joblib.load(stage2_path)
                if mapping_path.exists():
                    self.category_mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
                self.mode = "real_model"
                logger.info("Inference mode: real_model")
            else:
                self.mode = "mock"
                logger.info("Inference mode: mock (artifacts missing)")
        except Exception as exc:
            self.mode = "mock"
            logger.warning("Falling back to mock inference: %s", exc)

    def predict_category(self, article_text: str, provided_category: str | None = None) -> tuple[str, float]:
        if self.mode == "real_model" and self.stage1_vectorizer is not None and self.stage1_model is not None:
            features = self.stage1_vectorizer.transform([article_text])
            prediction = self.stage1_model.predict(features)[0]
            confidence = 0.8
            if hasattr(self.stage1_model, "predict_proba"):
                probabilities = self.stage1_model.predict_proba(features)[0]
                confidence = float(max(probabilities))
            return str(self.category_mapping.get(str(prediction), prediction)), round(confidence, 4)

        return self._mock_predict_category(article_text=article_text, provided_category=provided_category)

    def score_stage2(self, feature_vector: dict) -> float:
        if self.mode == "real_model" and self.stage2_model is not None:
            ordered = [[
                feature_vector["stage1_confidence"],
                feature_vector["category_match"],
                feature_vector["text_similarity"],
                feature_vector["behaviour_score"],
                feature_vector["session_page_count"],
                feature_vector["same_category_views"],
                feature_vector["dwell_time_seconds"],
                feature_vector["scroll_depth_ratio"],
                feature_vector["engagement_score"],
                feature_vector["ad_type_targeted"],
            ]]
            return float(self.stage2_model.predict(ordered)[0])

        return round(
            feature_vector["category_match"] * 0.35
            + feature_vector["text_similarity"] * 0.1
            + feature_vector["behaviour_score"] * 0.2
            + feature_vector["stage1_confidence"] * 0.15
            + feature_vector["engagement_score"] * 0.1
            + feature_vector["ad_type_targeted"] * 0.1,
            4,
        )

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
