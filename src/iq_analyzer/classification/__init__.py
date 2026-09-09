"""Classification module."""

from .classifier import ModulationClassifier, ClassifierConfig, create_default_classifier
from .training import (
    TrainingConfig,
    TrainingData,
    generate_training_data,
    extract_feature_matrix,
    train_model,
    evaluate_model,
    cross_validate_model,
    save_model,
    run_training_pipeline,
)
from .prediction import (
    predict_single,
    predict_batch,
    predict_from_file,
    analyze_classification_confidence,
    get_class_probabilities,
)
from .model_registry import (
    ModelRegistry,
    ModelInfo,
    create_model_info,
)

__all__ = [
    "ModulationClassifier",
    "ClassifierConfig",
    "create_default_classifier",
    "TrainingConfig",
    "TrainingData",
    "generate_training_data",
    "extract_feature_matrix",
    "train_model",
    "evaluate_model",
    "cross_validate_model",
    "save_model",
    "run_training_pipeline",
    "predict_single",
    "predict_batch",
    "predict_from_file",
    "analyze_classification_confidence",
    "get_class_probabilities",
    "ModelRegistry",
    "ModelInfo",
    "create_model_info",
]