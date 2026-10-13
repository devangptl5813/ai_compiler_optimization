"""
Validate and Filter Module
Validates all downloaded C programs:
1. Compiles with gcc -O0 through -Os (timeout 30s)
2. Executes across flags (timeout 2s per run) to ensure clean termination (returncode 0)
3. Detects and filters out duplicate feature vectors (near-duplicate detection)
4. Quarantines failed programs to programs_failed/
5. Generates validation report: total_downloaded, total_passed, total_failed, failure_reasons
6. Logs all actions to logs/expand_log.txt
"""

import os
import sys
import shutil
import time
import subprocess
import datetime
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add src to path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(BASE_DIR, "src"))

from feature_extractor import extract_features

PROGRAMS_DIR = os.path.join(BASE_DIR, "programs")
FAILED_DIR = os.path.join(BASE_DIR, "programs_failed")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOGS_DIR, "expand_log.txt")
REPORT_FILE = os.path.join(LOGS_DIR, "validation_report.json")
MANIFEST_PATH = os.path.join(BASE_DIR, "manifest.json")

os.makedirs(FAILED_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)


def log_msg(msg: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")


def validate_single_program(filename: str, worker_id: int) -> dict:
    """
    Compiles and executes a single program across -O0 through -Os.
    Returns validation result dict.
    """
    filepath = os.path.join(PROGRAMS_DIR, filename)
    if not os.path.exists(filepath):
        return {"filename": filename, "status": "FAILED", "reason": "File does not exist"}

    flags = ["O0", "O1", "O2", "O3", "Os"]
    flag_results = []

    for flag in flags:
        gcc_flag = f"-{flag}"
        base_name = os.path.splitext(filename)[0]
        temp_exe = os.path.join(PROGRAMS_DIR, f"_val_w{worker_id}_{base_name}_{flag}.exe")

        if os.path.exists(temp_exe):
            try:
                os.remove(temp_exe)
            except Exception:
                pass

        # 1. Compilation check (30s timeout)
        t_comp_start = time.perf_counter()
        try:
            comp_proc = subprocess.run(
                ["gcc", gcc_flag, filepath, "-o", temp_exe, "-lm"],
                capture_output=True,
                text=True,
                timeout=30
            )
            t_comp = time.perf_counter() - t_comp_start
            if comp_proc.returncode != 0:
                err_snippet = comp_proc.stderr.strip()[:200].replace("\n", " ")
                return {
                    "filename": filename,
                    "status": "FAILED",
                    "reason": f"Compilation failed under {gcc_flag}: {err_snippet}"
                }
        except subprocess.TimeoutExpired:
            return {
                "filename": filename,
                "status": "FAILED",
                "reason": f"Compilation timed out (>30s) under {gcc_flag}"
            }
        except Exception as e:
            return {
                "filename": filename,
                "status": "FAILED",
                "reason": f"Compilation error under {gcc_flag}: {str(e)}"
            }

        if not os.path.exists(temp_exe):
            return {
                "filename": filename,
                "status": "FAILED",
                "reason": f"Binary missing after compilation under {gcc_flag}"
            }

        # Measure binary size
        try:
            bsize = os.path.getsize(temp_exe)
        except Exception:
            bsize = 0

        # 2. Execution check (2s timeout per run, 3 runs for median)
        exec_times = []
        for run_idx in range(3):
            try:
                t_run_start = time.perf_counter()
                exec_proc = subprocess.run(
                    [temp_exe],
                    capture_output=True,
                    text=True,
                    timeout=2.0
                )
                t_run = time.perf_counter() - t_run_start
                if exec_proc.returncode != 0:
                    if os.path.exists(temp_exe):
                        try:
                            os.remove(temp_exe)
                        except Exception:
                            pass
                    return {
                        "filename": filename,
                        "status": "FAILED",
                        "reason": f"Execution crashed with exit code {exec_proc.returncode} under {gcc_flag}"
                    }
                exec_times.append(t_run)
            except subprocess.TimeoutExpired:
                if os.path.exists(temp_exe):
                    try:
                        os.remove(temp_exe)
                    except Exception:
                        pass
                return {
                    "filename": filename,
                    "status": "FAILED",
                    "reason": f"Execution timed out (>2.0s) under {gcc_flag}"
                }
            except Exception as e:
                if os.path.exists(temp_exe):
                    try:
                        os.remove(temp_exe)
                    except Exception:
                        pass
                return {
                    "filename": filename,
                    "status": "FAILED",
                    "reason": f"Execution error under {gcc_flag}: {str(e)}"
                }

        # Clean up binary
        if os.path.exists(temp_exe):
            try:
                os.remove(temp_exe)
            except Exception:
                pass

        exec_times.sort()
        median_exec = exec_times[len(exec_times) // 2]
        flag_results.append({
            "flag": flag,
            "compile_time": round(t_comp, 5),
            "exec_time": round(median_exec, 5),
            "binary_size": bsize
        })

    # Determine best flag: lowest exec_time, tie-break binary_size
    sorted_flags = sorted(flag_results, key=lambda x: (x["exec_time"], x["binary_size"]))
    best_flag = sorted_flags[0]["flag"]

    return {
        "filename": filename,
        "status": "PASSED",
        "best_flag": best_flag,
        "flag_results": flag_results
    }


def validate_all_programs(num_workers: int = 6):
    log_msg("=" * 70)
    log_msg("STARTING STEP 3: VALIDATE & FILTER DOWNLOADED PROGRAMS")
    log_msg("=" * 70)

    # 1. Identify all programs in programs/
    all_files = sorted([f for f in os.listdir(PROGRAMS_DIR) if f.endswith(".c")])
    baseline_files = [f for f in all_files if not f.startswith(("polybench_", "cbench_", "mibench_", "beebs_", "llvm_testsuite_"))]
    new_files = [f for f in all_files if f.startswith(("polybench_", "cbench_", "mibench_", "beebs_", "llvm_testsuite_"))]

    total_downloaded = len(new_files)
    log_msg(f"Baseline programs detected: {len(baseline_files)}")
    log_msg(f"New programs to validate:   {total_downloaded}")

    # 2. Extract features from baseline programs to initialize duplicate-detection cache
    seen_feature_vectors = {}
    for bfile in baseline_files:
        bpath = os.path.join(PROGRAMS_DIR, bfile)
        feats = extract_features(bpath)
        vec = tuple(feats[k] for k in sorted(feats.keys()))
        seen_feature_vectors[vec] = bfile

    log_msg(f"Initialized duplicate cache with {len(seen_feature_vectors)} baseline feature vectors.")

    cache_path = os.path.join(LOGS_DIR, "validated_measurements_cache.json")
    passed_programs = {}
    failed_programs = []
    failure_reasons = {}

    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                passed_programs = json.load(f)
            log_msg(f"Loaded existing validation cache: {len(passed_programs)} programs already PASSED.")
            # Add feature vectors of already passed programs into duplicate cache
            for pf in passed_programs.keys():
                ppath = os.path.join(PROGRAMS_DIR, pf)
                if os.path.exists(ppath):
                    pfeats = extract_features(ppath)
                    pvec = tuple(pfeats[k] for k in sorted(pfeats.keys()))
                    seen_feature_vectors[pvec] = pf
        except Exception as e:
            log_msg(f"Could not load previous measurements cache: {e}")

    # Load existing report failure reasons if present
    if os.path.exists(REPORT_FILE):
        try:
            with open(REPORT_FILE, "r", encoding="utf-8") as f:
                prev_rep = json.load(f)
                failure_reasons = prev_rep.get("failure_reasons", {})
                failed_programs = prev_rep.get("failed_programs", [])
        except Exception:
            pass

    # Filter out files that already passed
    untested_new_files = [f for f in new_files if f not in passed_programs]
    log_msg(f"Untested new programs to validate: {len(untested_new_files)}")

    def record_failure(fname: str, reason: str):
        failed_programs.append({"filename": fname, "reason": reason})
        cat = reason.split(":")[0]
        failure_reasons[cat] = failure_reasons.get(cat, 0) + 1
        # Quarantine file to programs_failed/
        src = os.path.join(PROGRAMS_DIR, fname)
        dst = os.path.join(FAILED_DIR, fname)
        if os.path.exists(src):
            try:
                shutil.move(src, dst)
            except Exception as e:
                log_msg(f"Error moving {fname} to quarantine: {e}")

    # 3. Near-duplicate pre-check & size check
    valid_candidates = []
    log_msg("Checking for duplicate feature vectors and file size limits...")
    for idx, nfile in enumerate(untested_new_files, 1):
        npath = os.path.join(PROGRAMS_DIR, nfile)
        if not os.path.exists(npath):
            continue

        # File size check
        fsize = os.path.getsize(npath)
        if fsize > 500 * 1024:
            record_failure(nfile, f"File size too large ({fsize} bytes > 500KB)")
            continue

        feats = extract_features(npath)
        vec = tuple(feats[k] for k in sorted(feats.keys()))
        if vec in seen_feature_vectors:
            match_file = seen_feature_vectors[vec]
            record_failure(nfile, f"Duplicate feature vector of {match_file}")
        else:
            seen_feature_vectors[vec] = nfile
            valid_candidates.append(nfile)

        if idx % 100 == 0:
            log_msg(f"  Duplicate check progress: [{idx}/{len(new_files)}]")

    log_msg(f"Near-duplicate check complete: {len(valid_candidates)} unique candidates ({len(failed_programs)} quarantined).")

    # 4. Multi-threaded compilation & execution validation
    log_msg(f"Starting compilation and execution validation with {num_workers} worker threads...")
    completed_count = 0
    total_candidates = len(valid_candidates)

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_file = {
            executor.submit(validate_single_program, fname, idx % num_workers): fname
            for idx, fname in enumerate(valid_candidates)
        }

        for future in as_completed(future_to_file):
            fname = future_to_file[future]
            completed_count += 1
            try:
                res = future.result()
                if res["status"] == "PASSED":
                    passed_programs[fname] = res
                else:
                    record_failure(fname, res["reason"])
            except Exception as exc:
                record_failure(fname, f"Validation exception: {str(exc)}")

            if completed_count % 50 == 0 or completed_count == total_candidates:
                log_msg(f"  Progress: [{completed_count}/{total_candidates}] validated (Passed: {len(passed_programs)}, Failed: {len(failed_programs)})")

    total_passed = len(passed_programs)
    total_failed = len(failed_programs)

    log_msg("=" * 70)
    log_msg("VALIDATION & FILTERING REPORT:")
    log_msg(f"  Total downloaded: {total_downloaded}")
    log_msg(f"  Total passed:     {total_passed}")
    log_msg(f"  Total failed:     {total_failed}")
    log_msg("  Failure reasons breakdown:")
    for cat, count in sorted(failure_reasons.items(), key=lambda x: -x[1]):
        log_msg(f"    - {cat}: {count}")
    log_msg("=" * 70)

    # Save validation report
    report_data = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_downloaded": total_downloaded,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "failure_reasons": failure_reasons,
        "passed_programs": list(passed_programs.keys()),
        "failed_programs": failed_programs,
        "passed_details": passed_programs
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
    log_msg(f"Saved validation report -> {REPORT_FILE}")

    # Also save cached measurements for Step 4
    cache_path = os.path.join(LOGS_DIR, "validated_measurements_cache.json")
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(passed_programs, f, indent=2)
    log_msg(f"Saved validated measurements cache -> {cache_path}")

    return report_data


if __name__ == "__main__":
    validate_all_programs()
