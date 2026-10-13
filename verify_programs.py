import os
import subprocess
import sys
import time

programs_dir = "programs"
c_files = sorted([f for f in os.listdir(programs_dir) if f.endswith(".c")])

print(f"Testing compilation and execution for {len(c_files)} programs...", flush=True)
failed = []

for c_file in c_files:
    src_path = os.path.join(programs_dir, c_file)
    exe_name = f"temp_{c_file[:-2]}.exe"
    exe_path = os.path.join(programs_dir, exe_name)
    
    if os.path.exists(exe_path):
        try:
            os.remove(exe_path)
        except Exception:
            pass
            
    comp = subprocess.run(["gcc", "-O2", src_path, "-o", exe_path], capture_output=True, text=True)
    if comp.returncode != 0:
        print(f"FAILED Compilation: {c_file} | Error: {comp.stderr.strip()}", flush=True)
        failed.append(c_file)
        continue
        
    try:
        run_res = subprocess.run([exe_path], capture_output=True, text=True, timeout=5)
        if run_res.returncode != 0:
            print(f"FAILED Execution: {c_file} | Code: {run_res.returncode}", flush=True)
            failed.append(c_file)
        else:
            print(f"OK: {c_file}", flush=True)
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT: {c_file}", flush=True)
        failed.append(c_file)
    
    if os.path.exists(exe_path):
        try:
            os.remove(exe_path)
        except Exception:
            pass

print(f"Finished verification. Failed/Slow programs: {failed}", flush=True)
