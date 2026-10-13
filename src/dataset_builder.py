"""
Dataset Builder Module
Iterates through benchmark C programs, extracts enhanced static features, compiles and measures
performance across all GCC optimization levels (O0, O1, O2, O3, Os) using median timing over 10 runs,
and outputs data/dataset.csv and data/raw_performance.csv.
"""

import os
import sys
import pandas as pd
import logging

# Ensure src directory is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from feature_extractor import extract_features
from compiler_runner import compile_and_measure

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def build_dataset(programs_dir: str = "programs", data_dir: str = "data") -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Builds the dataset by extracting static features and running benchmark measurements.

    Args:
        programs_dir: Directory containing .c benchmark programs.
        data_dir: Directory to save generated CSV files.

    Returns:
        tuple (dataset_df, raw_perf_df)
    """
    os.makedirs(data_dir, exist_ok=True)
    c_files = sorted([f for f in os.listdir(programs_dir) if f.endswith(".c")])
    total_files = len(c_files)

    if total_files == 0:
        logging.error(f"No .c files found in '{programs_dir}'!")
        return pd.DataFrame(), pd.DataFrame()

    logging.info(f"Starting dataset creation for {total_files} C programs...")

    flags = ["O0", "O1", "O2", "O3", "Os"]
    dataset_rows = []
    raw_perf_rows = []

    for idx, filename in enumerate(c_files, start=1):
        filepath = os.path.join(programs_dir, filename)
        logging.info(f"[{idx}/{total_files}] Processing '{filename}'...")

        # 1. Extract static features
        features = extract_features(filepath)

        # 2. Compile and measure for each flag (median over 10 runs)
        flag_results = []
        for flag in flags:
            res = compile_and_measure(filepath, flag, num_exec_runs=10)
            if res:
                raw_perf_rows.append({
                    "program": filename,
                    "flag": res["opt_flag"],
                    "compile_time": res["compile_time"],
                    "exec_time": res["exec_time"],
                    "binary_size": res["binary_size"]
                })
                flag_results.append(res)
            else:
                logging.warning(f"Failed measurement for {filename} under flag -{flag}")

        if not flag_results:
            logging.error(f"Skipping {filename} due to all flag compilation/execution failures.")
            continue

        # 3. Determine best flag (lowest exec_time, tie-break by binary_size)
        sorted_results = sorted(flag_results, key=lambda x: (x["exec_time"], x["binary_size"]))
        best_flag = sorted_results[0]["opt_flag"]

        row = {"program": filename}
        row.update(features)
        row["best_flag"] = best_flag
        dataset_rows.append(row)

    # 4. Create DataFrames and save CSV files
    dataset_df = pd.DataFrame(dataset_rows)
    raw_perf_df = pd.DataFrame(raw_perf_rows)

    dataset_path = os.path.join(data_dir, "dataset.csv")
    raw_perf_path = os.path.join(data_dir, "raw_performance.csv")

    dataset_df.to_csv(dataset_path, index=False)
    raw_perf_df.to_csv(raw_perf_path, index=False)

    logging.info(f"Saved dataset CSV ({len(dataset_df)} rows) -> '{dataset_path}'")
    logging.info(f"Saved raw performance CSV ({len(raw_perf_df)} rows) -> '{raw_perf_path}'")

    return dataset_df, raw_perf_df


if __name__ == "__main__":
    df, raw_df = build_dataset()
    print("\n" + "=" * 80)
    print(f"Dataset generated successfully! ({len(df)} rows)")
    print("=" * 80)
    print("\nFirst 15 rows of data/dataset.csv:\n")
    print(df.head(15).to_string(index=False))
