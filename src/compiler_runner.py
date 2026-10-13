"""
Compiler Runner Module
Compiles C programs with specified GCC optimization flags (-O0, -O1, -O2, -O3, -Os)
and measures compile time, output binary size, and execution time (using median over 10 runs for stability).
"""

import os
import sys
import time
import subprocess
import logging
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def compile_and_measure(filepath: str, opt_flag: str, num_exec_runs: int = 10) -> dict | None:
    """
    Compiles a C file with a specific optimization flag and measures performance metrics.

    Args:
        filepath: Path to the .c source file.
        opt_flag: Optimization flag (e.g. "O0", "O1", "O2", "O3", "Os" or "-O0").
        num_exec_runs: Number of execution runs to compute median timing over (default 10).

    Returns:
        dict: Performance metrics or None if compilation/execution failed.
    """
    if not os.path.exists(filepath):
        logging.error(f"Source file not found: {filepath}")
        return None

    # Normalize flag format
    flag_str = opt_flag.lstrip('-')
    gcc_flag = f"-{flag_str}"

    base_name = os.path.splitext(os.path.basename(filepath))[0]
    out_binary = os.path.join(os.path.dirname(filepath), f"temp_{base_name}_{flag_str}.exe")

    # Clean previous binary if exists
    if os.path.exists(out_binary):
        try:
            os.remove(out_binary)
        except Exception:
            pass

    # 1. Compile and measure compile time
    compile_start = time.perf_counter()
    try:
        comp_proc = subprocess.run(
            ["gcc", gcc_flag, filepath, "-o", out_binary, "-lm"],
            capture_output=True,
            text=True,
            timeout=30
        )
        compile_end = time.perf_counter()
        compile_time = compile_end - compile_start

        if comp_proc.returncode != 0:
            logging.error(f"Compilation failed for {filepath} with flag {gcc_flag}: {comp_proc.stderr}")
            return None

    except Exception as e:
        logging.error(f"Compilation error for {filepath} with {gcc_flag}: {e}")
        return None

    if not os.path.exists(out_binary):
        logging.error(f"Compiled binary path does not exist: {out_binary}")
        return None

    # 2. Measure binary size
    try:
        binary_size = os.path.getsize(out_binary)
    except Exception as e:
        logging.error(f"Could not read binary size for {out_binary}: {e}")
        binary_size = 0

    # 3. Measure execution time (median of num_exec_runs for stability)
    exec_times = []
    for run in range(num_exec_runs):
        try:
            run_start = time.perf_counter()
            exec_proc = subprocess.run(
                [out_binary],
                capture_output=True,
                text=True,
                timeout=10
            )
            run_end = time.perf_counter()

            if exec_proc.returncode != 0:
                logging.error(f"Execution failed for {out_binary}: {exec_proc.stderr}")
                if os.path.exists(out_binary):
                    try:
                        os.remove(out_binary)
                    except Exception:
                        pass
                return None

            exec_times.append(run_end - run_start)

        except subprocess.TimeoutExpired:
            logging.error(f"Execution timed out for {out_binary} (Run {run+1})")
            if os.path.exists(out_binary):
                try:
                    os.remove(out_binary)
                except Exception:
                    pass
            return None
        except Exception as e:
            logging.error(f"Execution error for {out_binary}: {e}")
            if os.path.exists(out_binary):
                try:
                    os.remove(out_binary)
                except Exception:
                    pass
            return None

    # Clean up output binary
    if os.path.exists(out_binary):
        try:
            os.remove(out_binary)
        except Exception as e:
            logging.warning(f"Could not remove temporary binary {out_binary}: {e}")

    median_exec_time = float(np.median(exec_times)) if exec_times else 0.0

    return {
        "opt_flag": flag_str,
        "compile_time": round(compile_time, 5),
        "exec_time": round(median_exec_time, 5),
        "binary_size": binary_size
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join("programs", "matrix_mult.c")
    flags = ["O0", "O1", "O2", "O3", "Os"]
    print(f"Testing compiler_runner (median over 10 runs) on '{target}':")
    print(f"{'Flag':<8}{'Compile Time (s)':<20}{'Exec Time (s)':<18}{'Binary Size (bytes)':<20}")
    print("-" * 66)

    for flag in flags:
        res = compile_and_measure(target, flag, num_exec_runs=10)
        if res:
            print(f"-{res['opt_flag']:<7}{res['compile_time']:<20.5f}{res['exec_time']:<18.5f}{res['binary_size']:<20}")
        else:
            print(f"-{flag:<7} FAILED")
