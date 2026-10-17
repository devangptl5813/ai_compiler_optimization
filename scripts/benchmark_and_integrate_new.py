"""
Benchmark and Integrate New Generator Programs
Measures newly generated C benchmark programs across GCC optimization levels (-O0, -O1, -O2, -O3, -Os),
extracts static features, computes optimal flags, and safely appends records to:
- data/raw_performance.csv
- data/dataset.csv
- data/dataset_with_sources.csv
- data/dataset.json
- manifest.json
"""

import os
import sys
import json
import datetime
import pandas as pd
import numpy as np

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(BASE_DIR, "src"))

from feature_extractor import extract_features
from compiler_runner import compile_and_measure

PROGRAMS_DIR = os.path.join(BASE_DIR, "programs")
DATA_DIR = os.path.join(BASE_DIR, "data")
DATASET_CSV = os.path.join(DATA_DIR, "dataset.csv")
DATASET_SOURCES_CSV = os.path.join(DATA_DIR, "dataset_with_sources.csv")
DATASET_JSON = os.path.join(DATA_DIR, "dataset.json")
RAW_PERF_CSV = os.path.join(DATA_DIR, "raw_performance.csv")
MANIFEST_FILE = os.path.join(BASE_DIR, "manifest.json")

NEW_PROGRAMS = [
    "gemm_blocked.c",
    "sobel_filter.c",
    "radix_sort.c",
    "avl_tree_ops.c",
    "sparse_matrix_csr.c",
    "astar_pathfind.c",
    "crc64_calc.c",
    "sudoku_solver.c",
    "gaussian_blur.c",
    "lru_cache_sim.c"
]

def main():
    print("=" * 70)
    print("BENCHMARKING & INTEGRATING 10 NEW C PROGRAMS INTO DATASET")
    print("=" * 70)

    # 1. Read existing dataset to check for duplicates
    existing_df = pd.read_csv(DATASET_CSV)
    existing_programs = set(existing_df["program"].tolist())
    print(f"Loaded existing dataset: {len(existing_df)} programs.")

    to_benchmark = [p for p in NEW_PROGRAMS if p not in existing_programs]
    if not to_benchmark:
        print("All new programs already present in dataset.csv! Nothing to do.")
        return

    print(f"Programs to benchmark and integrate ({len(to_benchmark)}): {to_benchmark}\n")

    flags = ["O0", "O1", "O2", "O3", "Os"]
    new_dataset_rows = []
    new_raw_perf_rows = []
    manifest_updates = []
    today_str = datetime.date.today().isoformat()

    for idx, filename in enumerate(to_benchmark, start=1):
        filepath = os.path.join(PROGRAMS_DIR, filename)
        if not os.path.exists(filepath):
            print(f"[{idx}/{len(to_benchmark)}] File missing: {filepath}")
            continue

        print(f"[{idx}/{len(to_benchmark)}] Benchmarking '{filename}'...")

        # Feature extraction
        features = extract_features(filepath)

        # Compilation & performance measurements across flags
        flag_results = []
        for flag in flags:
            res = compile_and_measure(filepath, flag, num_exec_runs=5)
            if res:
                new_raw_perf_rows.append({
                    "program": filename,
                    "flag": res["opt_flag"],
                    "compile_time": res["compile_time"],
                    "exec_time": res["exec_time"],
                    "binary_size": res["binary_size"]
                })
                flag_results.append(res)
                print(f"    [-{flag}] exec: {res['exec_time']:.4f}s, size: {res['binary_size']} bytes")
            else:
                print(f"    [-{flag}] FAILED measurement")

        if not flag_results:
            print(f"  --> SKIPPING {filename}: all flags failed.")
            continue

        # Choose best flag (lowest execution time, tie-break by binary size)
        sorted_results = sorted(flag_results, key=lambda x: (x["exec_time"], x["binary_size"]))
        best_flag = sorted_results[0]["opt_flag"]
        print(f"  --> Optimal flag for '{filename}': -{best_flag} (time: {sorted_results[0]['exec_time']:.4f}s)\n")

        row = {"program": filename}
        row.update(features)
        row["best_flag"] = best_flag
        new_dataset_rows.append(row)

        manifest_updates.append({
            "program": filename,
            "source": "original_30",
            "original_path": f"programs/{filename}",
            "license": "Internal / Benchmark Suite",
            "date_added": today_str
        })

    if not new_dataset_rows:
        print("No valid new records to append.")
        return

    # Append to dataset.csv
    new_df = pd.DataFrame(new_dataset_rows)
    updated_dataset_df = pd.concat([existing_df, new_df], ignore_index=True)
    updated_dataset_df.to_csv(DATASET_CSV, index=False)
    print(f"[+] Appended {len(new_df)} rows to {DATASET_CSV} (Total: {len(updated_dataset_df)} rows)")

    # Append to dataset_with_sources.csv
    if os.path.exists(DATASET_SOURCES_CSV):
        sources_df = pd.read_csv(DATASET_SOURCES_CSV)
        new_sources_df = new_df.copy()
        new_sources_df["source"] = "original_30"
        updated_sources_df = pd.concat([sources_df, new_sources_df], ignore_index=True)
        updated_sources_df.to_csv(DATASET_SOURCES_CSV, index=False)
        print(f"[+] Appended {len(new_sources_df)} rows to {DATASET_SOURCES_CSV}")

    # Append to raw_performance.csv
    if new_raw_perf_rows and os.path.exists(RAW_PERF_CSV):
        raw_df = pd.read_csv(RAW_PERF_CSV)
        new_raw_df = pd.DataFrame(new_raw_perf_rows)
        updated_raw_df = pd.concat([raw_df, new_raw_df], ignore_index=True)
        updated_raw_df.to_csv(RAW_PERF_CSV, index=False)
        print(f"[+] Appended {len(new_raw_df)} measurements to {RAW_PERF_CSV}")

    # Update dataset.json
    if os.path.exists(DATASET_JSON):
        with open(DATASET_JSON, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        for r in new_dataset_rows:
            r_copy = dict(r)
            r_copy["source"] = "original_30"
            json_data.append(r_copy)
        with open(DATASET_JSON, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)
        print(f"[+] Updated {DATASET_JSON}")

    # Update manifest.json
    if os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
        manifest_data.extend(manifest_updates)
        with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)
        print(f"[+] Updated {MANIFEST_FILE}")

    print("\nBenchmark and dataset integration complete!")

if __name__ == "__main__":
    main()
