"""Model registry for tracking trained models."""

import json
import joblib
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class ModelInfo:
    """Information about a registered model."""

    model_id: str
    model_path: str
    model_name: str
    version: str
    feature_version: str
    training_date: str
    classes: List[str]
    training_config: Dict[str, Any]
    evaluation_metrics: Dict[str, Any]
    dataset_version: str
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelInfo":
        return cls(**data)


class ModelRegistry:
    """Registry for managing trained models."""

    def __init__(self, registry_path: Path):
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.registry_path / "model_index.json"
        self.models: Dict[str, ModelInfo] = {}
        self._load_index()

    def _load_index(self) -> None:
        """Load model index from disk."""
        if self.index_file.exists():
            try:
                with open(self.index_file) as f:
                    data = json.load(f)
                self.models = {k: ModelInfo.from_dict(v) for k, v in data.items()}
            except Exception as e:
                logger.warning(f"Failed to load model index: {e}")
                self.models = {}

    def _save_index(self) -> None:
        """Save model index to disk."""
        data = {k: v.to_dict() for k, v in self.models.items()}
        with open(self.index_file, "w") as f:
            json.dump(data, f, indent=2)

    def register_model(
        self,
        model_path: Path,
        model_info: ModelInfo,
        copy_model: bool = True,
    ) -> str:
        """
        Register a model in the registry.

        Args:
            model_path: Path to model file
            model_info: Model metadata
            copy_model: Whether to copy model to registry directory

        Returns:
            Model ID
        """
        model_id = model_info.model_id

        if copy_model:
            dest_path = self.registry_path / f"{model_id}.joblib"
            import shutil
            shutil.copy2(model_path, dest_path)
            model_info.model_path = str(dest_path)

        self.models[model_id] = model_info
        self._save_index()

        logger.info(f"Registered model: {model_id}")
        return model_id

    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        """Get model info by ID."""
        return self.models.get(model_id)

    def list_models(self) -> List[ModelInfo]:
        """List all registered models."""
        return list(self.models.values())

    def find_compatible_model(
        self,
        feature_version: str,
        required_classes: Optional[List[str]] = None,
    ) -> Optional[ModelInfo]:
        """
        Find a model compatible with the given feature version and classes.

        Args:
            feature_version: Required feature version
            required_classes: List of required classes (subset of model classes)

        Returns:
            Compatible ModelInfo or None
        """
        compatible = []

        for model in self.models.values():
            if model.feature_version != feature_version:
                continue

            if required_classes:
                model_classes = set(model.classes)
                if not set(required_classes).issubset(model_classes):
                    continue

            compatible.append(model)

        if not compatible:
            return None

        # Return the newest model
        return max(compatible, key=lambda m: m.training_date)

    def load_model(self, model_id: str) -> Any:
        """Load model by ID."""
        model_info = self.get_model(model_id)
        if model_info is None:
            raise ValueError(f"Model not found: {model_id}")

        model_data = joblib.load(model_info.model_path)
        return model_data

    def delete_model(self, model_id: str) -> bool:
        """Delete a model from registry."""
        if model_id not in self.models:
            return False

        model_info = self.models[model_id]
        try:
            Path(model_info.model_path).unlink(missing_ok=True)
        except Exception:
            pass

        del self.models[model_id]
        self._save_index()
        return True

    def export_registry(self, output_path: Path) -> None:
        """Export registry to JSON file."""
        data = {k: v.to_dict() for k, v in self.models.items()}
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)


def create_model_info(
    model_path: Path,
    model_name: str,
    version: str,
    feature_version: str,
    classes: List[str],
    training_config: Dict[str, Any],
    evaluation_metrics: Dict[str, Any],
    dataset_version: str,
    description: str = "",
) -> ModelInfo:
    """Create ModelInfo from training results."""
    model_id = f"{model_name}_v{version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    return ModelInfo(
        model_id=model_id,
        model_path=str(model_path),
        model_name=model_name,
        version=version,
        feature_version=feature_version,
        training_date=datetime.now().isoformat(),
        classes=classes,
        training_config=training_config,
        evaluation_metrics=evaluation_metrics,
        dataset_version=dataset_version,
        description=description,
    )