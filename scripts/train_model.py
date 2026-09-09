#!/usr/bin/env python
"""Train modulation classification model."""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from iq_analyzer.classification import run_training_pipeline, TrainingConfig
from iq_analyzer.config import settings


def main():
    parser = argparse.ArgumentParser(description="Train modulation classification model")
    parser.add_argument("dataset_dir", type=Path, help="Dataset directory")
    parser.add_argument("output_model", type=Path, help="Output model path")
    parser.add_argument("--model-type", choices=["random_forest", "svm"], default="random_forest")
    parser.add_argument("--n-estimators", type=int, default=200)
    parser.add_argument("--max-depth", type=int, default=20)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--cv-folds", type=int, default=5)
    parser.add_argument("--max-samples-per-class", type=int, help="Limit samples per class")
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()

    config = TrainingConfig(
        model_type=args.model_type,
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        test_size=args.test_size,
        cv_folds=args.cv_folds,
        random_state=args.seed,
    )

    print(f"Training {args.model_type} model on {args.dataset_dir}...")
    results = run_training_pipeline(
        dataset_path=args.dataset_dir,
        output_path=args.output_model,
        config=config,
    )

    print("\nTraining complete!")
    print(f"Model saved to: {results['model_path']}")
    print(f"Samples: {results['num_samples']}")
    print(f"Features: {results['num_features']}")
    print(f"Classes: {results['num_classes']} ({', '.join(results['classes'])})")
    print(f"Accuracy: {results['evaluation']['accuracy']:.4f}")
    print(f"CV Score: {results['cross_validation']['cv_mean']:.4f} ± {results['cross_validation']['cv_std']:.4f}")


if __name__ == "__main__":
    main()