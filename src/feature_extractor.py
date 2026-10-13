"""
Feature Extractor Module
Extracts comprehensive static code features from C/C++ source code files.
Includes loop nesting depth, pointer ops, division/modulo count, ratios, and recursion detection.
"""

import os
import re
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def max_nesting_depth(content: str) -> int:
    """Calculates the maximum loop nesting depth in the C content."""
    max_depth = 0
    current_depth = 0
    open_braces = 0
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped.startswith('for') or stripped.startswith('while'):
            current_depth += 1
            max_depth = max(max_depth, current_depth)
        if '{' in stripped:
            open_braces += stripped.count('{')
        if '}' in stripped:
            close_count = stripped.count('}')
            open_braces -= close_count
            if open_braces < 0:
                current_depth = max(0, current_depth - close_count)
                open_braces = 0
    return max_depth


def nested_loop_count(content: str) -> int:
    """Counts instances of loops inside loops."""
    pattern = r'(for|while).*?\{[^}]*(for|while).*?\{'
    return len(re.findall(pattern, content, re.DOTALL))


def extract_features(filepath: str) -> dict:
    """
    Parses a .c file and extracts informative numerical static code features.
    """
    default_features = {
        "num_lines": 0,
        "file_size_bytes": 0,
        "code_lines": 0,
        "num_loops": 0,
        "num_functions": 0,
        "num_branches": 0,
        "num_arithmetic_ops": 0,
        "num_pointers": 0,
        "num_arrays": 0,
        "num_function_calls": 0,
        "max_loop_nesting_depth": 0,
        "num_div_mod_ops": 0,
        "num_recursive_calls": 0,
        "num_dynamic_alloc": 0,
        "num_structs": 0,
        "num_pointer_ops": 0,
        "num_nested_loops": 0,
        "branch_density": 0.0,
        "loop_per_function": 0.0,
        "arithmetic_per_line": 0.0,
        "call_branch_ratio": 0.0
    }

    if not os.path.exists(filepath):
        logging.error(f"File not found: {filepath}")
        return default_features

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        lines = content.split('\n')
        total_lines = len(lines)
        code_lines = [l for l in lines if l.strip() and not l.strip().startswith('//') and not l.strip().startswith('/*')]

        features = {}
        features["num_lines"] = total_lines
        features["file_size_bytes"] = os.path.getsize(filepath)
        features["code_lines"] = len(code_lines)

        # Basic static features
        features["num_loops"] = len(re.findall(r'\b(for|while)\b', content))
        features["num_functions"] = len(re.findall(r'\b\w+\s+\w+\s*\([^)]*\)\s*\{', content))
        features["num_branches"] = len(re.findall(r'\b(if|else|switch|case)\b', content))
        features["num_arithmetic_ops"] = len(re.findall(r'(?<!\w)[\+\-\*/\%](?!\w)', content))
        features["num_pointers"] = len(re.findall(r'\*\s*\w+', content))
        features["num_arrays"] = len(re.findall(r'\[\d+\]|\[[^\]]+\]', content))
        features["num_function_calls"] = len(re.findall(r'\w+\s*\([^;]*\)\s*;', content))

        # Advanced structural features
        features["max_loop_nesting_depth"] = max_nesting_depth(content)
        features["num_div_mod_ops"] = len(re.findall(r'[\/%]', content))

        # Recursion detection
        func_defs = re.findall(r'(?:void|int|float|double|char|long)\s+(\w+)\s*\([^)]*\)\s*\{', content)
        recursive_count = 0
        for func_name in func_defs:
            if re.search(r'\b' + re.escape(func_name) + r'\s*\(', content):
                # Count calls to itself inside body
                recursive_count += len(re.findall(r'\b' + re.escape(func_name) + r'\s*\(', content)) - 1
        features["num_recursive_calls"] = max(0, recursive_count)

        # Dynamic memory allocation
        features["num_dynamic_alloc"] = len(re.findall(r'\b(malloc|calloc|realloc|free)\b', content))

        # Struct/typedef usage
        features["num_structs"] = len(re.findall(r'\b(typedef\s+)?struct\b', content))

        # Pointer arithmetic & dereferences
        features["num_pointer_ops"] = len(re.findall(r'[*&]\s*\w+|->', content))

        # Nested loops count
        features["num_nested_loops"] = nested_loop_count(content)

        # Ratios
        features["branch_density"] = round(features["num_branches"] / max(features["num_lines"], 1), 4)
        features["loop_per_function"] = round(features["num_loops"] / max(features["num_functions"], 1), 4)
        features["arithmetic_per_line"] = round(features["num_arithmetic_ops"] / max(features["num_lines"], 1), 4)
        features["call_branch_ratio"] = round(features["num_function_calls"] / max(features["num_branches"], 1), 4)

        return features

    except Exception as e:
        logging.error(f"Error extracting features from {filepath}: {e}")
        return default_features


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join("programs", "matrix_mult.c")
    features = extract_features(target)
    print(f"Features extracted from '{target}':")
    for k, v in features.items():
        print(f"  {k}: {v}")
