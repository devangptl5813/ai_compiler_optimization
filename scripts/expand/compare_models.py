"""
Model Comparison Module
Compares Old Model (31 baseline samples) vs New Model (641 expanded samples):
1. Accuracy (Train, Test)
2. F1 score per class (O0, O1, O2, O3, Os)
3. Overfitting gap (Train Acc - Test Acc)
4. Oracle match rate & latency comparison
Outputs comparison table to results/model_comparison.txt and logs/expand_log.txt.
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, accuracy_score

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OLD_MODEL_PATH = os.path.join(BASE_DIR, "models", "model_v1_backup.pkl")
NEW_MODEL_PATH = os.path.join(BASE_DIR, "models", "model.pkl")
OUT_TXT = os.path.join(BASE_DIR, "results", "model_comparison.txt")
LOG_FILE = os.path.join(BASE_DIR, "logs", "expand_log.txt")


def compare():
    if not (os.path.exists(OLD_MODEL_PATH) and os.path.exists(NEW_MODEL_PATH)):
        print("Missing model files.")
        return

    # 1. Old Model
    old_art = joblib.load(OLD_MODEL_PATH)
    old_model = old_art["model"]
    old_cols = old_art["feature_cols"]
    old_test_idx = old_art["test_indices"]
    old_df = old_art["all_data"]

    old_test = old_df.loc[old_test_idx]
    old_train = old_df.drop(old_test_idx)

    old_train_preds = old_model.predict(old_train[old_cols])
    old_test_preds = old_model.predict(old_test[old_cols])

    old_train_acc = accuracy_score(old_train["best_flag"], old_train_preds)
    old_test_acc = accuracy_score(old_test["best_flag"], old_test_preds)
    old_gap = old_train_acc - old_test_acc
    old_rep = classification_report(old_test["best_flag"], old_test_preds, output_dict=True, zero_division=0)

    # 2. New Model
    new_art = joblib.load(NEW_MODEL_PATH)
    new_model = new_art["model"]
    new_cols = new_art["feature_cols"]
    new_test_idx = new_art["test_indices"]
    new_df = new_art["all_data"]

    new_test = new_df.loc[new_test_idx]
    new_train = new_df.drop(new_test_idx)

    new_train_preds = new_model.predict(new_train[new_cols])
    new_test_preds = new_model.predict(new_test[new_cols])

    new_train_acc = accuracy_score(new_train["best_flag"], new_train_preds)
    new_test_acc = accuracy_score(new_test["best_flag"], new_test_preds)
    new_gap = new_train_acc - new_test_acc
    new_rep = classification_report(new_test["best_flag"], new_test_preds, output_dict=True, zero_division=0)

    # Classes
    classes = ["O0", "O1", "O2", "O3", "Os"]

    lines = []
    lines.append("=" * 75)
    lines.append("          MODEL COMPARISON: OLD (31 SAMPLES) vs NEW (641 SAMPLES)          ")
    lines.append("=" * 75)
    lines.append(f"{'Metric':<30}{'Old Model (31 samples)':<24}{'New Model (641 samples)':<24}")
    lines.append("-" * 75)
    lines.append(f"{'Dataset Size':<30}{len(old_df):<24}{len(new_df):<24}")
    lines.append(f"{'Train / Test Split':<30}{f'{len(old_train)} / {len(old_test)}':<24}{f'{len(new_train)} / {len(new_test)}':<24}")
    lines.append(f"{'Test Accuracy':<30}{f'{old_test_acc:.2%}':<24}{f'{new_test_acc:.2%}':<24}")
    lines.append(f"{'Train Accuracy':<30}{f'{old_train_acc:.2%}':<24}{f'{new_train_acc:.2%}':<24}")
    lines.append(f"{'Overfitting Gap':<30}{f'{old_gap:.2%}':<24}{f'{new_gap:.2%}':<24}")
    lines.append("-" * 75)
    lines.append("PER-CLASS F1 SCORES:")
    for c in classes:
        old_f1 = old_rep.get(c, {}).get("f1-score", 0.0)
        new_f1 = new_rep.get(c, {}).get("f1-score", 0.0)
        lines.append(f"{'  F1 Score (-' + c + ')':<30}{f'{old_f1:.2f}':<24}{f'{new_f1:.2f}':<24}")
    lines.append("-" * 75)
    old_macro = old_rep["macro avg"]["f1-score"]
    new_macro = new_rep["macro avg"]["f1-score"]
    old_weighted = old_rep["weighted avg"]["f1-score"]
    new_weighted = new_rep["weighted avg"]["f1-score"]
    lines.append(f"{'Macro Avg F1':<30}{old_macro:<24.2f}{new_macro:<24.2f}")
    lines.append(f"{'Weighted Avg F1':<30}{old_weighted:<24.2f}{new_weighted:<24.2f}")
    lines.append("=" * 75)

    text = "\n".join(lines)
    print("\n" + text + "\n")

    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write(text)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n" + text + "\n")


if __name__ == "__main__":
    compare()
