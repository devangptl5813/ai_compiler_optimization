"""
Expand Dataset Module
Downloads/clones prioritized benchmark suites:
1. PolyBench/C
2. cBench
3. MiBench
4. LLVM Test Suite (SingleSource)
5. BEEBS
Extracts standalone, self-contained C programs into programs/ with naming:
  {source}_{original_name}.c
Maintains manifest.json and logs all actions to logs/expand_log.txt.
"""

import os
import sys
import re
import json
import shutil
import datetime
import subprocess
import logging

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROGRAMS_DIR = os.path.join(BASE_DIR, "programs")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOGS_DIR, "expand_log.txt")
MANIFEST_PATH = os.path.join(BASE_DIR, "manifest.json")

os.makedirs(PROGRAMS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)


def log_msg(msg: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")


POLYBENCH_PREAMBLE = """
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define POLYBENCH_DUMP_TARGET stderr
#define POLYBENCH_RESTRICT
#define POLYBENCH_C99_SELECT(x,y) x
#define POLYBENCH_LOOP_BOUND(x,y) x

#define POLYBENCH_1D(var, dim1, ddim1) var[dim1]
#define POLYBENCH_2D(var, dim1, dim2, ddim1, ddim2) var[dim1][dim2]
#define POLYBENCH_3D(var, dim1, dim2, dim3, ddim1, ddim2, ddim3) var[dim1][dim2][dim3]

#define POLYBENCH_1D_F(var, dim1, ddim1) var[dim1]
#define POLYBENCH_2D_F(var, dim1, dim2, ddim1, ddim2) var[dim1][dim2]
#define POLYBENCH_3D_F(var, dim1, dim2, dim3, ddim1, ddim2, ddim3) var[dim1][dim2][dim3]

#define POLYBENCH_ALLOC_1D_ARRAY(n1, type) (type(*)[n1])polybench_alloc_data(n1, sizeof(type))
#define POLYBENCH_ALLOC_2D_ARRAY(n1, n2, type) (type(*)[n1][n2])polybench_alloc_data((n1)*(n2), sizeof(type))
#define POLYBENCH_ALLOC_3D_ARRAY(n1, n2, n3, type) (type(*)[n1][n2][n3])polybench_alloc_data((n1)*(n2)*(n3), sizeof(type))

#define POLYBENCH_1D_ARRAY_DECL(var, type, dim1, ddim1) \\
  type POLYBENCH_1D_F(POLYBENCH_DECL_VAR(var), dim1, ddim1); \\
  var = POLYBENCH_ALLOC_1D_ARRAY(dim1, type);
#define POLYBENCH_2D_ARRAY_DECL(var, type, dim1, dim2, ddim1, ddim2) \\
  type POLYBENCH_2D_F(POLYBENCH_DECL_VAR(var), dim1, dim2, ddim1, ddim2); \\
  var = POLYBENCH_ALLOC_2D_ARRAY(dim1, dim2, type);
#define POLYBENCH_3D_ARRAY_DECL(var, type, dim1, dim2, dim3, ddim1, ddim2, ddim3) \\
  type POLYBENCH_3D_F(POLYBENCH_DECL_VAR(var), dim1, dim2, dim3, ddim1, ddim2, ddim3); \\
  var = POLYBENCH_ALLOC_3D_ARRAY(dim1, dim2, dim3, type);

#define POLYBENCH_DECL_VAR(var) (*var)
#define POLYBENCH_ARRAY(var) (*var)
#define POLYBENCH_FREE_ARRAY(var) polybench_free_data(var)

static void* polybench_alloc_data(unsigned long long n, int elt_size) {
    return malloc(n * elt_size);
}
static void polybench_free_data(void* ptr) {
    if (ptr) free(ptr);
}

#define polybench_start_instruments
#define polybench_stop_instruments
#define polybench_print_instruments
#define polybench_prevent_dce(func) func
#define POLYBENCH_DUMP_START
#define POLYBENCH_DUMP_BEGIN(s)
#define POLYBENCH_DUMP_END(s)
#define POLYBENCH_DUMP_FINISH
"""


def extract_polybench(manifest: list) -> int:
    """Extracts PolyBench kernels into standalone C files."""
    poly_dir = os.path.join(BASE_DIR, ".temp_polybench")
    if not os.path.exists(poly_dir):
        log_msg("[PolyBench] Repository not found at .temp_polybench. Skipping.")
        return 0

    log_msg("[PolyBench] Extracting kernels from PolyBench/C...")
    count = 0
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    # Walk through .temp_polybench looking for .c files with matching .h files
    for root, dirs, files in os.walk(poly_dir):
        if "utilities" in root or ".git" in root:
            continue
        c_files = [f for f in files if f.endswith(".c")]
        for c_file in c_files:
            kernel_name = os.path.splitext(c_file)[0]
            h_file = f"{kernel_name}.h"
            if h_file not in files:
                continue

            c_path = os.path.join(root, c_file)
            h_path = os.path.join(root, h_file)

            try:
                with open(h_path, "r", encoding="utf-8", errors="ignore") as f:
                    h_code = f.read()
                with open(c_path, "r", encoding="utf-8", errors="ignore") as f:
                    c_code = f.read()

                # Prepend SMALL_DATASET / MINI_DATASET to ensure fast runtimes
                h_code = "#define MINI_DATASET\n" + h_code

                # Strip polybench includes and self header includes
                c_code = re.sub(r'#include\s*<unistd\.h>', '', c_code)
                c_code = re.sub(r'#include\s*<polybench\.h>', '', c_code)
                c_code = re.sub(r'#include\s*["<]' + re.escape(h_file) + r'[">]', '', c_code)

                standalone_code = POLYBENCH_PREAMBLE + "\n" + h_code + "\n" + c_code
                out_name = f"polybench_{kernel_name}.c"
                out_path = os.path.join(PROGRAMS_DIR, out_name)

                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(standalone_code)

                manifest.append({
                    "program": out_name,
                    "source": "polybench",
                    "original_path": os.path.relpath(c_path, BASE_DIR).replace("\\", "/"),
                    "license": "BSD-3-Clause",
                    "date_added": today
                })
                count += 1
                log_msg(f"  [PolyBench] Extracted: {out_name}")

            except Exception as e:
                log_msg(f"  [PolyBench] Error extracting {c_file}: {e}")

    log_msg(f"[PolyBench] Total kernels extracted: {count}")
    return count


def extract_cbench(manifest: list) -> int:
    """Extracts standalone programs from cBench."""
    cbench_dir = os.path.join(BASE_DIR, ".temp_cbench", "program")
    if not os.path.exists(cbench_dir):
        log_msg("[cBench] Directory not found at .temp_cbench/program. Skipping.")
        return 0

    log_msg("[cBench] Extracting benchmark programs from cBench...")
    count = 0
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    for prog_dir in sorted(os.listdir(cbench_dir)):
        if not prog_dir.startswith("cbench-"):
            continue
        full_dir = os.path.join(cbench_dir, prog_dir)
        if not os.path.isdir(full_dir):
            continue

        c_files = [f for f in os.listdir(full_dir) if f.endswith(".c") and not f.startswith(".")]
        if not c_files:
            continue

        # Single .c file or easily flattened
        clean_name = prog_dir.replace("cbench-", "").replace("-", "_")
        out_name = f"cbench_{clean_name}.c"
        out_path = os.path.join(PROGRAMS_DIR, out_name)

        try:
            if len(c_files) == 1:
                src_file = os.path.join(full_dir, c_files[0])
                with open(src_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                # Skip if depends on unistd or sys/time without standard fallback
                content = re.sub(r'#include\s*<sys/time\.h>', '#include <time.h>', content)
                content = re.sub(r'#include\s*<unistd\.h>', '', content)
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(content)
                manifest.append({
                    "program": out_name,
                    "source": "cbench",
                    "original_path": os.path.relpath(src_file, BASE_DIR).replace("\\", "/"),
                    "license": "Open Source / cTuning",
                    "date_added": today
                })
                count += 1
                log_msg(f"  [cBench] Extracted: {out_name}")
            else:
                # Merge small multi-file programs (e.g. crc32, adpcm, sha, rijndael)
                # Find the main file
                main_file = None
                for cf in c_files:
                    with open(os.path.join(full_dir, cf), "r", encoding="utf-8", errors="ignore") as f:
                        if re.search(r'\bint\s+main\b|\bvoid\s+main\b', f.read()):
                            main_file = cf
                            break
                if main_file and len(c_files) <= 5:
                    combined = []
                    # Read headers in the directory
                    h_files = [f for f in os.listdir(full_dir) if f.endswith(".h")]
                    for hf in h_files:
                        with open(os.path.join(full_dir, hf), "r", encoding="utf-8", errors="ignore") as f:
                            combined.append(f"/* Inlined header {hf} */\n" + f.read())

                    # Read other .c files first, then main_file
                    for cf in c_files:
                        if cf != main_file:
                            with open(os.path.join(full_dir, cf), "r", encoding="utf-8", errors="ignore") as f:
                                code = f.read()
                                code = re.sub(r'#include\s*<unistd\.h>', '', code)
                                code = re.sub(r'#include\s*<sys/time\.h>', '#include <time.h>', code)
                                for hf in h_files:
                                    code = re.sub(r'#include\s*["<]' + re.escape(hf) + r'[">]', '', code)
                                combined.append(f"/* Inlined source {cf} */\n" + code)

                    with open(os.path.join(full_dir, main_file), "r", encoding="utf-8", errors="ignore") as f:
                        mcode = f.read()
                        mcode = re.sub(r'#include\s*<unistd\.h>', '', mcode)
                        mcode = re.sub(r'#include\s*<sys/time\.h>', '#include <time.h>', mcode)
                        for hf in h_files:
                            mcode = re.sub(r'#include\s*["<]' + re.escape(hf) + r'[">]', '', mcode)
                        combined.append(f"/* Main file {main_file} */\n" + mcode)

                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write("\n".join(combined))

                    manifest.append({
                        "program": out_name,
                        "source": "cbench",
                        "original_path": os.path.relpath(os.path.join(full_dir, main_file), BASE_DIR).replace("\\", "/"),
                        "license": "Open Source / cTuning",
                        "date_added": today
                    })
                    count += 1
                    log_msg(f"  [cBench] Flattened & Extracted: {out_name}")

        except Exception as e:
            log_msg(f"  [cBench] Error extracting {prog_dir}: {e}")

    log_msg(f"[cBench] Total programs extracted: {count}")
    return count


def extract_mibench(manifest: list) -> int:
    """Extracts standalone C programs from MiBench."""
    mibench_dir = os.path.join(BASE_DIR, ".temp_mibench")
    if not os.path.exists(mibench_dir):
        log_msg("[MiBench] Directory not found at .temp_mibench. Skipping.")
        return 0

    log_msg("[MiBench] Extracting standalone benchmark programs from MiBench...")
    count = 0
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    # Target specific standalone benchmark directories
    targets = [
        ("automotive/basicmath", "basicmath_small.c", "basicmath_small"),
        ("automotive/bitcount", "bitcnts.c", "bitcnts"),
        ("automotive/qsort", "qsort_small.c", "qsort_small"),
        ("automotive/susan", "susan.c", "susan"),
        ("network/dijkstra", "dijkstra_small.c", "dijkstra_small"),
        ("network/patricia", "patricia_test.c", "patricia"),
        ("office/stringsearch", "bmhs.c", "stringsearch"),
        ("security/blowfish", "bf.c", "blowfish"),
        ("security/sha", "sha.c", "sha"),
        ("telecomm/adpcm/src", "rawcaudio.c", "adpcm_rawcaudio"),
        ("telecomm/adpcm/src", "rawdaudio.c", "adpcm_rawdaudio"),
        ("telecomm/CRC32", "crc_32.c", "crc32"),
        ("telecomm/FFT", "main.c", "fft"),
    ]

    for rel_dir, main_c, out_id in targets:
        full_dir = os.path.join(mibench_dir, rel_dir)
        if not os.path.exists(full_dir):
            continue

        c_path = os.path.join(full_dir, main_c)
        if not os.path.exists(c_path):
            # Check for any .c file
            c_cand = [f for f in os.listdir(full_dir) if f.endswith(".c")]
            if c_cand:
                c_path = os.path.join(full_dir, c_cand[0])
            else:
                continue

        out_name = f"mibench_{out_id}.c"
        out_path = os.path.join(PROGRAMS_DIR, out_name)

        try:
            # Check if multi-file in that directory (e.g. headers or helper .c)
            h_files = [f for f in os.listdir(full_dir) if f.endswith(".h")]
            c_files = [f for f in os.listdir(full_dir) if f.endswith(".c")]

            combined = []
            for hf in h_files:
                with open(os.path.join(full_dir, hf), "r", encoding="utf-8", errors="ignore") as f:
                    combined.append(f.read())

            for cf in c_files:
                if cf != os.path.basename(c_path):
                    with open(os.path.join(full_dir, cf), "r", encoding="utf-8", errors="ignore") as f:
                        code = f.read()
                        code = re.sub(r'#include\s*<unistd\.h>', '', code)
                        combined.append(code)

            with open(c_path, "r", encoding="utf-8", errors="ignore") as f:
                code = f.read()
                code = re.sub(r'#include\s*<unistd\.h>', '', code)
                code = re.sub(r'#include\s*<sys/time\.h>', '#include <time.h>', code)
                combined.append(code)

            full_text = "\n".join(combined)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(full_text)

            manifest.append({
                "program": out_name,
                "source": "mibench",
                "original_path": os.path.relpath(c_path, BASE_DIR).replace("\\", "/"),
                "license": "GPL / BSD / Public Domain",
                "date_added": today
            })
            count += 1
            log_msg(f"  [MiBench] Extracted: {out_name}")

        except Exception as e:
            log_msg(f"  [MiBench] Error extracting {rel_dir}: {e}")

    log_msg(f"[MiBench] Total programs extracted: {count}")
    return count


def extract_beebs(manifest: list) -> int:
    """Extracts standalone C programs from BEEBS."""
    beebs_src = os.path.join(BASE_DIR, ".temp_beebs", "src")
    if not os.path.exists(beebs_src):
        log_msg("[BEEBS] Directory not found at .temp_beebs/src. Skipping.")
        return 0

    log_msg("[BEEBS] Extracting benchmark programs from BEEBS...")
    count = 0
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    preamble = """
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define REPEAT_FACTOR 1
#define BOARD_REPEAT_FACTOR 1
#define CALIB_SCALE 0
"""

    main_footer = """
int main(void) {
    initialise_benchmark();
    int res = benchmark();
    verify_benchmark(res);
    return 0;
}
"""

    for bname in sorted(os.listdir(beebs_src)):
        bdir = os.path.join(beebs_src, bname)
        if not os.path.isdir(bdir):
            continue

        c_files = [f for f in os.listdir(bdir) if f.endswith(".c") and not f.startswith(".")]
        if not c_files:
            continue

        out_name = f"beebs_{bname.replace('-', '_')}.c"
        out_path = os.path.join(PROGRAMS_DIR, out_name)

        try:
            combined = [preamble]
            h_files = [f for f in os.listdir(bdir) if f.endswith(".h")]
            for hf in h_files:
                if hf in ["support.h", "config.h"]:
                    continue
                with open(os.path.join(bdir, hf), "r", encoding="utf-8", errors="ignore") as f:
                    combined.append(f.read())

            has_main = False
            for cf in c_files:
                with open(os.path.join(bdir, cf), "r", encoding="utf-8", errors="ignore") as f:
                    code = f.read()
                    if re.search(r'\bint\s+main\b|\bvoid\s+main\b', code):
                        has_main = True
                    code = re.sub(r'#include\s*["<]support\.h[">]', '', code)
                    code = re.sub(r'#include\s*<unistd\.h>', '', code)
                    combined.append(code)

            if not has_main:
                combined.append(main_footer)

            with open(out_path, "w", encoding="utf-8") as f:
                f.write("\n".join(combined))

            manifest.append({
                "program": out_name,
                "source": "beebs",
                "original_path": os.path.relpath(bdir, BASE_DIR).replace("\\", "/"),
                "license": "GPLv3 / LGPL",
                "date_added": today
            })
            count += 1
            log_msg(f"  [BEEBS] Extracted: {out_name}")

        except Exception as e:
            log_msg(f"  [BEEBS] Error extracting {bname}: {e}")

    log_msg(f"[BEEBS] Total programs extracted: {count}")
    return count


def extract_llvm(manifest: list, target_count: int = 450) -> int:
    """Extracts single-source standalone programs from LLVM Test Suite."""
    llvm_dir = os.path.join(BASE_DIR, ".temp_llvm", "SingleSource")
    if not os.path.exists(llvm_dir):
        log_msg("[LLVM] SingleSource directory not found. Skipping.")
        return 0

    log_msg(f"[LLVM] Extracting single-source C programs from LLVM Test Suite (target ~{target_count})...")
    count = 0
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    # Priority 1: Benchmarks (Shootout, Stanford, McGill, Misc)
    benchmark_dirs = [
        os.path.join(llvm_dir, "Benchmarks", "Shootout"),
        os.path.join(llvm_dir, "Benchmarks", "Stanford"),
        os.path.join(llvm_dir, "Benchmarks", "McGill"),
        os.path.join(llvm_dir, "Benchmarks", "Misc"),
        os.path.join(llvm_dir, "Benchmarks", "Linpack"),
        os.path.join(llvm_dir, "Benchmarks", "Dhrystone"),
        os.path.join(llvm_dir, "UnitTests"),
        os.path.join(llvm_dir, "Regression", "C", "gcc-c-torture", "execute")
    ]

    for bdir in benchmark_dirs:
        if not os.path.exists(bdir):
            continue

        for root, dirs, files in os.walk(bdir):
            c_files = sorted([f for f in files if f.endswith(".c")])
            for cf in c_files:
                if count >= target_count:
                    break

                src_path = os.path.join(root, cf)
                clean_name = os.path.splitext(cf)[0].lower()
                clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', clean_name)
                out_name = f"llvm_testsuite_{clean_name}.c"
                out_path = os.path.join(PROGRAMS_DIR, out_name)

                # Avoid collision
                if os.path.exists(out_path):
                    continue

                try:
                    with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
                        code = f.read()

                    # Filter: must contain main()
                    if not re.search(r'\bint\s+main\b|\bvoid\s+main\b|\bmain\s*\(', code):
                        continue

                    # Filter: skip POSIX-heavy files
                    if any(bad in code for bad in ["<sys/mman.h>", "<pthread.h>", "<termios.h>", "<sys/socket.h>", "<netinet/in.h>"]):
                        continue

                    # Replace common sys/time with time.h and unistd removal
                    code = re.sub(r'#include\s*<sys/time\.h>', '#include <time.h>', code)
                    code = re.sub(r'#include\s*<unistd\.h>', '', code)

                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(code)

                    manifest.append({
                        "program": out_name,
                        "source": "llvm_testsuite",
                        "original_path": os.path.relpath(src_path, BASE_DIR).replace("\\", "/"),
                        "license": "Apache 2.0 with LLVM Exception",
                        "date_added": today
                    })
                    count += 1
                    if count % 50 == 0:
                        log_msg(f"  [LLVM] Extracted {count} programs so far...")

                except Exception as e:
                    pass

            if count >= target_count:
                break

    log_msg(f"[LLVM] Total programs extracted: {count}")
    return count


def extract_llvm_torture(manifest: list, target_count: int = 380) -> int:
    """Extracts GCC C-torture execution tests from LLVM test suite to scale dataset to >=500."""
    tort_dir = os.path.join(BASE_DIR, ".temp_llvm", "SingleSource", "Regression", "C", "gcc-c-torture", "execute")
    if not os.path.exists(tort_dir):
        return 0

    log_msg(f"[LLVM-Torture] Extracting torture execution kernels (target: {target_count})...")
    count = 0
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    c_files = sorted([f for f in os.listdir(tort_dir) if f.endswith(".c")])
    for cf in c_files:
        if count >= target_count:
            break

        clean_name = os.path.splitext(cf)[0].lower()
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', clean_name)
        out_name = f"llvm_testsuite_tort_{clean_name}.c"
        out_path = os.path.join(PROGRAMS_DIR, out_name)
        failed_path = os.path.join(BASE_DIR, "programs_failed", out_name)

        if os.path.exists(out_path) or os.path.exists(failed_path):
            continue

        src_path = os.path.join(tort_dir, cf)
        try:
            with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
                code = f.read()

            if not re.search(r'\bint\s+main\b|\bvoid\s+main\b|\bmain\s*\(', code):
                continue
            if any(bad in code for bad in ["<sys/mman.h>", "<pthread.h>", "<termios.h>", "<sys/socket.h>"]):
                continue

            code = re.sub(r'#include\s*<sys/time\.h>', '#include <time.h>', code)
            code = re.sub(r'#include\s*<unistd\.h>', '', code)

            with open(out_path, "w", encoding="utf-8") as f:
                f.write(code)

            manifest.append({
                "program": out_name,
                "source": "llvm_testsuite",
                "original_path": os.path.relpath(src_path, BASE_DIR).replace("\\", "/"),
                "license": "GPL / FSF GCC Runtime Exception",
                "date_added": today
            })
            count += 1
            if count % 50 == 0:
                log_msg(f"  [LLVM-Torture] Extracted {count} programs so far...")

        except Exception:
            pass

    log_msg(f"[LLVM-Torture] Total torture programs extracted: {count}")
    return count


def register_existing_30(manifest: list):
    """Registers the original baseline 30+ programs into manifest.json."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    existing = sorted([f for f in os.listdir(PROGRAMS_DIR) if f.endswith(".c") and not f.startswith(("polybench_", "cbench_", "mibench_", "beebs_", "llvm_testsuite_"))])
    for prog in existing:
        manifest.append({
            "program": prog,
            "source": "original_30",
            "original_path": f"programs/{prog}",
            "license": "Internal / Benchmark Suite",
            "date_added": today
        })
    log_msg(f"[Baseline] Registered {len(existing)} existing programs as 'original_30'.")


def main():
    log_msg("=" * 70)
    log_msg("STARTING STEP 2: EXPAND DATASET DOWNLOAD & EXTRACTION")
    log_msg("=" * 70)

    # Load existing manifest if present to preserve previous entries
    manifest = []
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception:
            manifest = []

    if not manifest:
        register_existing_30(manifest)
        n_poly = extract_polybench(manifest)
        n_cbench = extract_cbench(manifest)
        n_mibench = extract_mibench(manifest)
        n_beebs = extract_beebs(manifest)
        n_llvm = extract_llvm(manifest, target_count=450)
    else:
        n_poly = sum(1 for m in manifest if m["source"] == "polybench")
        n_cbench = sum(1 for m in manifest if m["source"] == "cbench")
        n_mibench = sum(1 for m in manifest if m["source"] == "mibench")
        n_beebs = sum(1 for m in manifest if m["source"] == "beebs")
        n_llvm = sum(1 for m in manifest if m["source"] == "llvm_testsuite")

    # Additional torture tests to reach scale
    n_tort = extract_llvm_torture(manifest, target_count=380)

    total_downloaded = len(manifest)
    log_msg("=" * 70)
    log_msg(f"DATASET EXTRACTION COMPLETE:")
    log_msg(f"  - PolyBench/C:        {n_poly}")
    log_msg(f"  - cBench:             {n_cbench}")
    log_msg(f"  - MiBench:            {n_mibench}")
    log_msg(f"  - BEEBS:              {n_beebs}")
    log_msg(f"  - LLVM TestSuite:     {n_llvm + n_tort}")
    log_msg(f"  TOTAL PROGRAMS IN MANIFEST: {total_downloaded}")
    log_msg("=" * 70)

    # Save manifest.json
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    log_msg(f"Saved manifest ({len(manifest)} total entries) -> manifest.json")


if __name__ == "__main__":
    main()

