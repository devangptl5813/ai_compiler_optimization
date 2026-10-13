"""
Predict Module
CLI tool to extract static features from a new C/C++ source file, load the trained ML model,
and predict the optimal GCC compiler optimization flag (-O0, -O1, -O2, -O3, -Os) along with confidence scores.
"""

import os
import sys
import argparse
import pandas as pd
import numpy as np
import joblib
import logging

# Add src to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from feature_extractor import extract_features

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def predict_best_flag(filepath: str, model_path: str = "models/model.pkl") -> dict | None:
    """
    Given a C source file path, predicts the best optimization flag and confidence scores.

    Args:
        filepath: Path to the target .c file.
        model_path: Path to serialized model artifact (models/model.pkl).

    Returns:
        dict with keys: 'predicted_flag', 'confidence_scores', 'features'
    """
    if not os.path.exists(filepath):
        logging.error(f"Target file not found: {filepath}")
        return None

    if not os.path.exists(model_path):
        logging.error(f"Trained model file not found: {model_path}. Run train_model.py first.")
        return None

    # Load serialized model package
    artifact = joblib.load(model_path)
    model = artifact["model"]
    feature_cols = artifact["feature_cols"]
    label_encoder = artifact.get("label_encoder", None)

    # Extract features from target C file
    features_dict = extract_features(filepath)
    input_df = pd.DataFrame([features_dict])[feature_cols]

    # Predict best flag
    if label_encoder is not None:
        pred_enc = model.predict(input_df)[0]
        predicted_flag = label_encoder.inverse_transform([pred_enc])[0]
        classes = label_encoder.classes_
    else:
        predicted_flag = model.predict(input_df)[0]
        classes = model.classes_

    # Get prediction confidence / probabilities
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(input_df)[0]
        confidence_scores = {str(cls): round(float(prob), 4) for cls, prob in zip(classes, probs)}
    else:
        confidence_scores = {str(cls): (1.0 if cls == predicted_flag else 0.0) for cls in classes}

    # Ensure flag starts with '-'
    clean_flag = f"-{predicted_flag.lstrip('-')}"

    return {
        "predicted_flag": clean_flag,
        "confidence_scores": confidence_scores,
        "features": features_dict
    }


def main():
    parser = argparse.ArgumentParser(description="Predict optimal GCC optimization flag for a C file.")
    parser.add_argument("--file", required=True, help="Path to input C/C++ source program")
    parser.add_argument("--model", default="models/model.pkl", help="Path to trained model.pkl")
    args = parser.parse_args()

    result = predict_best_flag(args.file, args.model)
    if result:
        print("\n" + "=" * 60)
        print(f"ML COMPILER OPTIMIZATION LEVEL PREDICTOR")
        print("=" * 60)
        print(f"Input file: {args.file}")
        print("-" * 60)
        print(f"Predicted best optimization flag: {result['predicted_flag']}")
        print(f"Confidence scores: {result['confidence_scores']}")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
