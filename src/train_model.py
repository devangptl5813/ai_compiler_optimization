"""
Train Model Module
Loads data/dataset.csv, splits into train/test sets, trains machine learning classifiers
(Random Forest and Gradient Boosting/XGBoost with class balancing), evaluates performance,
saves accuracy report to results/accuracy_report.txt, saves feature importances chart to
results/graphs/feature_importance.png, and serializes the best model + test set indices to models/model.pkl.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import logging

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def train_and_evaluate(data_path: str = "data/dataset.csv",
                       models_dir: str = "models",
                       results_dir: str = "results") -> dict:
    """
    Loads dataset, trains classifiers, evaluates performance, and saves artifacts with test set indices.

    Returns:
        dict containing metrics and trained model.
    """
    if not os.path.exists(data_path):
        logging.error(f"Dataset not found at '{data_path}'!")
        return {}

    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(os.path.join(results_dir, "graphs"), exist_ok=True)

    df = pd.read_csv(data_path)
    if df.empty:
        logging.error("Dataset CSV is empty!")
        return {}

    feature_cols = [c for c in df.columns if c not in ["program", "best_flag"]]
    X = df[feature_cols]
    y = df["best_flag"]

    # Try stratified split; fall back to unstratified if class count < 2
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,
            random_state=42,
            stratify=y
        )
    except ValueError:
        logging.warning("Stratified split failed (some class has <2 instances); falling back to random split.")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,
            random_state=42
        )

    logging.info(f"Dataset split: Train={len(X_train)} samples, Test={len(X_test)} samples.")

    models = {}
    
    # Model 1: Random Forest Classifier with class_weight='balanced'
    rf_model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight='balanced',
        min_samples_leaf=2,
        min_samples_split=3,
        max_depth=5
    )
    rf_model.fit(X_train, y_train)
    rf_preds = rf_model.predict(X_test)
    rf_acc = accuracy_score(y_test, rf_preds)
    models["RandomForest"] = {
        "model": rf_model,
        "acc": rf_acc,
        "preds": rf_preds,
        "report": classification_report(y_test, rf_preds, zero_division=0)
    }

    # Model 2: Try XGBoost or Fallback to GradientBoosting
    try:
        from xgboost import XGBClassifier
        le = LabelEncoder()
        y_train_enc = le.fit_transform(y_train)
        xgb = XGBClassifier(
            n_estimators=150,
            max_depth=4,
            learning_rate=0.05,
            random_state=42,
            eval_metric="mlogloss"
        )
        xgb.fit(X_train, y_train_enc)
        xgb_preds_enc = xgb.predict(X_test)
        xgb_preds = le.inverse_transform(xgb_preds_enc)
        xgb_acc = accuracy_score(y_test, xgb_preds)
        models["XGBoost"] = {
            "model": xgb,
            "label_encoder": le,
            "acc": xgb_acc,
            "preds": xgb_preds,
            "report": classification_report(y_test, xgb_preds, zero_division=0)
        }
    except ImportError:
        logging.info("XGBoost not available; using sklearn GradientBoostingClassifier as Model 2.")
        gb = GradientBoostingClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=3
        )
        gb.fit(X_train, y_train)
        gb_preds = gb.predict(X_test)
        gb_acc = accuracy_score(y_test, gb_preds)
        models["GradientBoosting"] = {
            "model": gb,
            "acc": gb_acc,
            "preds": gb_preds,
            "report": classification_report(y_test, gb_preds, zero_division=0)
        }

    # Select Best Model
    best_name = max(models, key=lambda k: models[k]["acc"])
    best_info = models[best_name]
    best_model = best_info["model"]

    logging.info(f"Trained Models evaluation:")
    for name, info in models.items():
        logging.info(f"  - {name}: Test Accuracy = {info['acc']:.2%}")

    logging.info(f"Selected best model: '{best_name}' with accuracy {best_info['acc']:.2%}")

    # FIX #1: Save test_indices and all_data inside model.pkl to guarantee evaluation sync!
    test_indices = X_test.index.tolist()
    model_path = os.path.join(models_dir, "model.pkl")
    joblib.dump({
        "model": best_model,
        "feature_cols": feature_cols,
        "model_name": best_name,
        "label_encoder": best_info.get("label_encoder", None),
        "test_indices": test_indices,
        "all_data": df
    }, model_path)
    logging.info(f"Saved trained model and test_indices to '{model_path}'")

    # Generate and Save Accuracy Report
    report_text = f"=" * 60 + "\n"
    report_text += f"ML COMPILER OPTIMIZATION LEVEL PREDICTOR - ACCURACY REPORT\n"
    report_text += f"=" * 60 + "\n\n"
    report_text += f"Dataset size: {len(df)} programs (Train={len(X_train)}, Test={len(X_test)})\n\n"

    for name, info in models.items():
        report_text += f"--- {name} Classifier ---\n"
        report_text += f"Accuracy: {info['acc']:.2%}\n"
        report_text += f"Classification Report:\n{info['report']}\n"
        report_text += "-" * 50 + "\n\n"

    report_text += f"BEST MODEL SAVED: {best_name} ({best_info['acc']:.2%} Test Accuracy)\n"

    report_file = os.path.join(results_dir, "accuracy_report.txt")
    with open(report_file, "w") as f:
        f.write(report_text)
    logging.info(f"Saved accuracy report -> '{report_file}'")

    # Plot Feature Importance Chart
    plt.figure(figsize=(10, 7))
    if hasattr(best_model, "feature_importances_"):
        importances = best_model.feature_importances_
    else:
        importances = np.ones(len(feature_cols)) / len(feature_cols)

    feat_imp = pd.Series(importances, index=feature_cols).sort_values(ascending=True)

    sns.barplot(x=feat_imp.values, y=feat_imp.index, hue=feat_imp.index, palette="viridis", legend=False)
    plt.title(f"Feature Importances ({best_name})", fontsize=14, fontweight="bold")
    plt.xlabel("Importance Score")
    plt.ylabel("Static Code Feature")
    plt.tight_layout()

    chart_path = os.path.join(results_dir, "graphs", "feature_importance.png")
    plt.savefig(chart_path, dpi=300)
    plt.close()
    logging.info(f"Saved feature importance chart -> '{chart_path}'")

    return {
        "best_name": best_name,
        "best_acc": best_info["acc"],
        "report_text": report_text,
        "chart_path": chart_path
    }


if __name__ == "__main__":
    res = train_and_evaluate()
    if res:
        print("\n" + res["report_text"])
