"""
Append to Dataset Module
Extracts static code features using src/feature_extractor.py on all validated programs.
Appends newly validated samples to data/dataset.csv and data/dataset.json:
- DO NOT overwrite or regenerate original baseline 31 entries.
- Preserves exact feature schema and column ordering.
- Maintains companion data/dataset_with_sources.csv and data/dataset.json with 'source' tagging.
"""

import os
import sys
import json
import datetime
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(BASE_DIR, "src"))

from feature_extractor import extract_features

PROGRAMS_DIR = os.path.join(BASE_DIR, "programs")
DATA_DIR = os.path.join(BASE_DIR, "data")
DATASET_CSV = os.path.join(DATA_DIR, "dataset.csv")
DATASET_JSON = os.path.join(DATA_DIR, "dataset.json")
DATASET_SOURCES_CSV = os.path.join(DATA_DIR, "dataset_with_sources.csv")
RAW_PERF_CSV = os.path.join(DATA_DIR, "raw_performance.csv")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOGS_DIR, "expand_log.txt")
CACHE_FILE = os.path.join(LOGS_DIR, "validated_measurements_cache.json")
MANIFEST_FILE = os.path.join(BASE_DIR, "manifest.json")


def log_msg(msg: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")


def determine_source(filename: str, manifest_map: dict) -> str:
    if filename in manifest_map:
        return manifest_map[filename]
    if filename.startswith("polybench_"):
        return "polybench"
    if filename.startswith("cbench_"):
        return "cbench"
    if filename.startswith("mibench_"):
        return "mibench"
    if filename.startswith("beebs_"):
        return "beebs"
    if filename.startswith("llvm_testsuite_"):
        return "llvm_testsuite"
    return "original_30"


def append_validated_to_dataset(include_source_in_main_csv: bool = False):
    log_msg("=" * 70)
    log_msg("STARTING STEP 4: RUN FEATURE EXTRACTION & APPEND TO DATASET")
    log_msg("=" * 70)

    # 1. Read existing dataset.csv
    if not os.path.exists(DATASET_CSV):
        log_msg(f"Error: {DATASET_CSV} does not exist!")
        return

    original_df = pd.read_csv(DATASET_CSV)
    existing_programs = set(original_df["program"].tolist())
    log_msg(f"Loaded existing dataset: {len(original_df)} baseline samples.")

    # Schema columns in original dataset
    original_cols = list(original_df.columns)
    log_msg(f"Original schema columns ({len(original_cols)}): {original_cols}")

    # 2. Load validated cache
    if not os.path.exists(CACHE_FILE):
        log_msg(f"Error: Validated cache {CACHE_FILE} not found! Run validate_programs.py first.")
        return

    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        validated_cache = json.load(f)

    # Load manifest
    manifest_map = {}
    if os.path.exists(MANIFEST_FILE):
        try:
            with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
                manifest_list = json.load(f)
            for item in manifest_list:
                manifest_map[item["program"]] = item["source"]
        except Exception:
            pass

    log_msg(f"Found {len(validated_cache)} validated programs in cache.")

    # 3. Extract features for new validated programs
    new_rows = []
    new_raw_perf_rows = []
    skipped_existing = 0

    for idx, (filename, val_info) in enumerate(validated_cache.items(), 1):
        if filename in existing_programs:
            skipped_existing += 1
            continue

        filepath = os.path.join(PROGRAMS_DIR, filename)
        if not os.path.exists(filepath):
            continue

        # Extract features using existing feature_extractor.py
        features = extract_features(filepath)
        best_flag = val_info.get("best_flag", "O2")
        source = determine_source(filename, manifest_map)

        row = {"program": filename}
        row.update(features)
        row["best_flag"] = best_flag
        row["source"] = source

        new_rows.append(row)

        # Also collect raw performance rows
        for res in val_info.get("flag_results", []):
            new_raw_perf_rows.append({
                "program": filename,
                "flag": res["flag"],
                "compile_time": res["compile_time"],
                "exec_time": res["exec_time"],
                "binary_size": res["binary_size"]
            })

        if len(new_rows) % 100 == 0:
            log_msg(f"  Extracted features for {len(new_rows)} new programs...")

    log_msg(f"Extraction complete: {len(new_rows)} new rows prepared ({skipped_existing} already existed).")

    if not new_rows:
        log_msg("No new rows to append.")
        return

    # 4. Construct DataFrames
    new_df = pd.DataFrame(new_rows)

    # Full DataFrame with source
    # For original rows, tag source as original_30 if not present
    if "source" not in original_df.columns:
        original_df_with_source = original_df.copy()
        original_df_with_source["source"] = "original_30"
    else:
        original_df_with_source = original_df.copy()

    combined_with_source = pd.concat([original_df_with_source, new_df], ignore_index=True)

    # Main dataset.csv DataFrame:
    if include_source_in_main_csv:
        # Include source column as requested in Step 4
        combined_df = combined_with_source
    else:
        # Keep exact 23 original schema columns
        base_cols = [c for c in original_cols if c != "source"]
        new_df_base = new_df[base_cols]
        combined_df = pd.concat([original_df[base_cols], new_df_base], ignore_index=True)

    # 5. Save dataset.csv, dataset_with_sources.csv, and dataset.json
    combined_df.to_csv(DATASET_CSV, index=False)
    combined_with_source.to_csv(DATASET_SOURCES_CSV, index=False)

    # Export dataset.json
    records = combined_with_source.to_dict(orient="records")
    with open(DATASET_JSON, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    # 6. Append to raw_performance.csv if present
    if os.path.exists(RAW_PERF_CSV) and new_raw_perf_rows:
        raw_df = pd.read_csv(RAW_PERF_CSV)
        new_raw_df = pd.DataFrame(new_raw_perf_rows)
        combined_raw = pd.concat([raw_df, new_raw_df], ignore_index=True)
        combined_raw.to_csv(RAW_PERF_CSV, index=False)
        log_msg(f"Updated raw performance log ({len(combined_raw)} total measurements) -> {RAW_PERF_CSV}")

    log_msg("=" * 70)
    log_msg("DATASET UPDATE COMPLETE:")
    log_msg(f"  - Original rows:      {len(original_df)}")
    log_msg(f"  - New rows appended:  {len(new_rows)}")
    log_msg(f"  - Total dataset rows: {len(combined_df)}")
    log_msg(f"  - Saved CSV:          {DATASET_CSV}")
    log_msg(f"  - Saved Source CSV:   {DATASET_SOURCES_CSV}")
    log_msg(f"  - Saved JSON:         {DATASET_JSON}")
    log_msg("=" * 70)


if __name__ == "__main__":
    include_source = "--include-source" in sys.argv
    append_validated_to_dataset(include_source_in_main_csv=include_source)
