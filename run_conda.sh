#!/bin/bash
# Small wrapper to run the project with the conda Python that has pandas installed.
# Usage: ./run_conda.sh [script-args]

PYTHON="/home/bonibb/python/miniconda3_py313/bin/python"
SCRIPT_DIR="$(dirname "$0")"

exec "$PYTHON" "$SCRIPT_DIR/src/extract_all.py" "$@"
