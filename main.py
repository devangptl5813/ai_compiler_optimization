"""
Main Orchestrator Module
Runs the full ML-Based Compiler Optimization Level Predictor pipeline end-to-end:
1. Builds labeled dataset from programs/ (feature extraction + compiler benchmarks)
2. Trains machine learning classifiers (Random Forest / XGBoost)
3. Evaluates predictions against fixed baselines (-O0, -O2, -O3) and Oracle optimal
4. Prints final summary report and saves all artifacts to results/
"""

import os
import sys
import time
import logging

# Add src/ directory to python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from dataset_builder import build_dataset
from train_model import train_and_evaluate
from evaluate import evaluate_pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main():
    start_time = time.time()
    print("\n" + "=" * 80)
    print("      ML-BASED COMPILER OPTIMIZATION LEVEL PREDICTOR - PIPELINE      ")
    print("=" * 80 + "\n")

    # Step 1: Build dataset
    print("[1/3] Extracting static features and compiling benchmark programs...")
    dataset_df, raw_df = build_dataset(programs_dir="programs", data_dir="data")
    if dataset_df.empty:
        print("Pipeline aborted: dataset generation failed.")
        sys.exit(1)
    print(f"-> Successfully generated dataset ({len(dataset_df)} programs, {len(raw_df)} total measurements).\n")

    # Step 2: Train ML Model
    print("[2/3] Training Machine Learning model(s)...")
    train_res = train_and_evaluate(data_path="data/dataset.csv", models_dir="models", results_dir="results")
    if not train_res:
        print("Pipeline aborted: model training failed.")
        sys.exit(1)
    print(f"-> Best model trained: '{train_res['best_name']}' (Accuracy: {train_res['best_acc']:.2%}).\n")

    # Step 3: Evaluate against Baselines
    print("[3/3] Evaluating ML-Predicted choices against GCC baselines (-O0, -O2, -O3)...")
    summary_df = evaluate_pipeline(data_path="data/dataset.csv", raw_perf_path="data/raw_performance.csv", model_path="models/model.pkl", results_dir="results")
    print("-> Evaluation complete! Comparison table and charts generated.\n")

    total_duration = time.time() - start_time

    # Final Summary Report
    print("=" * 80)
    print("                         FINAL SUMMARY REPORT                        ")
    print("=" * 80)
    print(summary_df.to_string(index=False))
    print("-" * 80)
    print(f"Pipeline finished successfully in {total_duration:.2f} seconds.")
    print(f"Artifacts saved:")
    print(f"  - Dataset CSV:             data/dataset.csv")
    print(f"  - Raw Performance Log:     data/raw_performance.csv")
    print(f"  - Trained Model:           models/model.pkl")
    print(f"  - Accuracy Report:         results/accuracy_report.txt")
    print(f"  - Strategy Comparison CSV: results/comparison_table.csv")
    print(f"  - Charts & Heatmaps:       results/graphs/")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
