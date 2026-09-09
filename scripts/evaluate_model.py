#!/usr/bin/env python
"""Evaluate trained modulation classification model."""

import argparse
import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from iq_analyzer.classification import predict_from_file, analyze_classification_confidence
from iq_analyzer.models import ModulationType
from iq_analyzer.utils import get_logger

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Evaluate modulation classification model")
    parser.add_argument("model_path", type=Path, help="Trained model path")
    parser.add_argument("test_dir", type=Path, help="Test dataset directory")
    parser.add_argument("--output", type=Path, help="Output results file")
    parser.add_argument("--confidence-threshold", type=float, default=0.5)

    args = parser.parse_args()

    # Find test files
    test_files = []
    true_labels = []

    for class_dir in args.test_dir.iterdir():
        if not class_dir.is_dir():
            continue
        try:
            mod_type = ModulationType(class_dir.name.upper())
        except ValueError:
            continue

        iq_files = list(class_dir.glob("*.iq"))
        for f in iq_files:
            test_files.append(f)
            true_labels.append(mod_type)

    if not test_files:
        print("No test files found!")
        return 1

    print(f"Evaluating on {len(test_files)} test files...")

    # Predict
    predictions = []
    for f in test_files:
        result = predict_from_file(f, args.model_path)
        predictions.append(result)

    # Analyze
    analysis = analyze_classification_confidence(predictions, args.confidence_threshold)

    # Compute accuracy by class
    correct = 0
    class_correct = {}
    class_total = {}

    for pred, true_label in zip(predictions, true_labels):
        class_total[true_label.value] = class_total.get(true_label.value, 0) + 1
        if pred.predicted_class == true_label:
            correct += 1
            class_correct[true_label.value] = class_correct.get(true_label.value, 0) + 1

    overall_accuracy = correct / len(predictions)
    print(f"\nOverall Accuracy: {overall_accuracy:.4f} ({correct}/{len(predictions)})")

    print("\nPer-class Accuracy:")
    for cls in sorted(class_total.keys()):
        total = class_total[cls]
        corr = class_correct.get(cls, 0)
        acc = corr / total if total > 0 else 0
        print(f"  {cls}: {acc:.4f} ({corr}/{total})")

    print(f"\nConfidence Analysis:")
    print(f"  Mean: {analysis['mean_confidence']:.4f}")
    print(f"  Std: {analysis['std_confidence']:.4f}")
    print(f"  High confidence (≥{args.confidence_threshold}): {analysis['high_confidence_count']}")
    print(f"  Low confidence (<{args.confidence_threshold}): {analysis['low_confidence_count']}")

    if args.output:
        import json
        output_data = {
            "overall_accuracy": overall_accuracy,
            "per_class": {
                cls: class_correct.get(cls, 0) / class_total[cls]
                for cls in class_total
            },
            "confidence_analysis": analysis,
        }
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"\nResults saved to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())