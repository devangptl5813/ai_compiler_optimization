"""
Evaluation Module
Compares ML-predicted compiler flag choice against fixed baseline strategies (-O0, -O2, -O3)
and the theoretical Oracle optimal strategy using measured raw performance logs.
Synchronizes test set via saved test_indices from train_model.py.
Exports comparison table to results/comparison_table.csv and creates visualization charts in results/graphs/.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import logging

from sklearn.metrics import confusion_matrix

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def evaluate_pipeline(data_path: str = "data/dataset.csv",
                      raw_perf_path: str = "data/raw_performance.csv",
                      model_path: str = "models/model.pkl",
                      results_dir: str = "results") -> pd.DataFrame:
    """
    Evaluates ML predictions against baseline compiler strategies (-O0, -O2, -O3) and Oracle.

    Returns:
        pd.DataFrame: Strategy comparison summary table.
    """
    if not (os.path.exists(data_path) and os.path.exists(raw_perf_path) and os.path.exists(model_path)):
        logging.error("Missing required data files or model artifact for evaluation.")
        return pd.DataFrame()

    os.makedirs(os.path.join(results_dir, "graphs"), exist_ok=True)

    # Load raw perf and model artifact
    raw_df = pd.read_csv(raw_perf_path)
    artifact = joblib.load(model_path)

    model = artifact["model"]
    feature_cols = artifact["feature_cols"]
    label_encoder = artifact.get("label_encoder", None)

    # FIX #1: Retrieve test_indices and all_data directly from artifact (no re-split!)
    test_indices = artifact["test_indices"]
    df = artifact["all_data"]
    test_df = df.loc[test_indices].copy()

    logging.info(f"Evaluating strategies on synced test set ({len(test_df)} programs)...")

    # Generate ML predictions for test set
    X_test = test_df[feature_cols]
    if label_encoder is not None:
        preds_enc = model.predict(X_test)
        test_df["ml_flag"] = label_encoder.inverse_transform(preds_enc)
    else:
        test_df["ml_flag"] = model.predict(X_test)

    # Helper lookup function from raw_performance.csv
    def get_perf(program_name: str, flag: str):
        flag_clean = flag.lstrip('-')
        match = raw_df[(raw_df["program"] == program_name) & (raw_df["flag"] == flag_clean)]
        if not match.empty:
            return match.iloc[0]["exec_time"], match.iloc[0]["binary_size"]
        return 0.0, 0

    # Define strategies
    strategies = ["Always -O0", "Always -O2", "Always -O3", "ML-Predicted", "Oracle (best possible)"]
    summary_data = []

    for strat in strategies:
        exec_times = []
        binary_sizes = []
        oracle_matches = 0

        for idx, row in test_df.iterrows():
            prog = row["program"]
            actual_best = row["best_flag"]

            if strat == "Always -O0":
                chosen_flag = "O0"
            elif strat == "Always -O2":
                chosen_flag = "O2"
            elif strat == "Always -O3":
                chosen_flag = "O3"
            elif strat == "ML-Predicted":
                chosen_flag = row["ml_flag"]
            elif strat == "Oracle (best possible)":
                chosen_flag = actual_best

            etime, bsize = get_perf(prog, chosen_flag)
            exec_times.append(etime)
            binary_sizes.append(bsize)

            if chosen_flag == actual_best:
                oracle_matches += 1

        avg_exec = np.mean(exec_times)
        avg_size = np.mean(binary_sizes)
        match_pct = (oracle_matches / len(test_df)) * 100.0

        summary_data.append({
            "Strategy": strat,
            "Avg Execution Time (s)": round(avg_exec, 5),
            "Avg Binary Size (bytes)": int(round(avg_size)),
            "% Programs Matched Oracle": round(match_pct, 2)
        })

    summary_df = pd.DataFrame(summary_data)

    # Save Comparison Table CSV
    table_path = os.path.join(results_dir, "comparison_table.csv")
    summary_df.to_csv(table_path, index=False)
    logging.info(f"Saved comparison table -> '{table_path}'")

    # 1. Bar Chart: Strategy Comparison (Avg Exec Time)
    plt.figure(figsize=(10, 6))
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#9b59b6', '#f1c40f']
    ax = sns.barplot(data=summary_df, x="Strategy", y="Avg Execution Time (s)", palette=colors, hue="Strategy", legend=False)
    plt.title("Compiler Optimization Strategies: Avg Execution Time (Test Set)", fontsize=13, fontweight="bold")
    plt.ylabel("Execution Time (seconds)")
    plt.xlabel("Strategy")
    plt.xticks(rotation=15)
    
    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.annotate(f'{height:.4f}s',
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom', fontsize=10, fontweight='bold', xytext=(0, 3),
                        textcoords='offset points')

    plt.tight_layout()
    chart1_path = os.path.join(results_dir, "graphs", "strategy_comparison.png")
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    logging.info(f"Saved strategy comparison graph -> '{chart1_path}'")

    # 2. Confusion Matrix Plot
    plt.figure(figsize=(8, 6))
    y_true = test_df["best_flag"]
    y_pred = test_df["ml_flag"]

    present_labels = sorted(list(set(y_true).union(set(y_pred))))
    cm = confusion_matrix(y_true, y_pred, labels=present_labels)

    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=[f"-{l}" for l in present_labels],
                yticklabels=[f"-{l}" for l in present_labels])
    plt.title("Confusion Matrix: Predicted vs Actual Best Flag", fontsize=13, fontweight="bold")
    plt.xlabel("ML-Predicted Flag")
    plt.ylabel("Actual Best Flag (Ground Truth)")
    plt.tight_layout()

    chart2_path = os.path.join(results_dir, "graphs", "confusion_matrix.png")
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    logging.info(f"Saved confusion matrix graph -> '{chart2_path}'")

    return summary_df


if __name__ == "__main__":
    res_df = evaluate_pipeline()
    print("\n" + "=" * 80)
    print("FINAL EVALUATION & STRATEGY COMPARISON TABLE")
    print("=" * 80)
    print(res_df.to_string(index=False))
    print("=" * 80 + "\n")
