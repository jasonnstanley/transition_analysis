"""Master build pipeline for the Transition Analysis Toolkit."""

from __future__ import annotations

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from python.build_log import log


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_stage(name: str, command: list[str]) -> bool:
    """Run one build stage and report whether it succeeded."""
    print()
    print("=" * 72)
    print(name)
    print("=" * 72)
    print("Command:", " ".join(command))
    print()

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=False,
    )

    if result.returncode == 0:
        print()
        print(f"{name}: PASS")
        return True

    print()
    print(f"{name}: FAIL — exit code {result.returncode}")
    return False


def main() -> int:
    """Run the reproducible research build pipeline."""
    started_at = datetime.now()
    start_time = time.perf_counter()

    print("=" * 72)
    print("Transition Analysis Toolkit — Master Build")
    print("=" * 72)
    print(f"Project root : {PROJECT_ROOT}")
    print(f"Started      : {started_at.isoformat(timespec='seconds')}")
    print(f"Python       : {sys.executable}")
    log("Build started")
    
    stages = [
        (
            "Stage 1 — Environment and project checks",
            [sys.executable, "-m", "python.checks"],
        ),
        (
            "Stage 2 — Python unit tests",
            [sys.executable, "-m", "pytest"],
        ),
    ]

    for stage_name, command in stages:
        log(f"Starting: {stage_name}")
        
        if not run_stage(stage_name, command):
            elapsed = time.perf_counter() - start_time
            
            print()
            print("=" * 72)
            print("BUILD FAILED")
            print("=" * 72)
            print(f"Failed stage : {stage_name}")
            print(f"Elapsed time : {elapsed:.2f} seconds")

            log(f"FAILED: {stage_name}")
            return 1
         
        log(f"PASSED: {stage_name}")
        
    log("Build completed successfully")
    
    finished_at = datetime.now()
    elapsed = time.perf_counter() - start_time

    print()
    print("=" * 72)
    print("BUILD COMPLETED SUCCESSFULLY")
    print("=" * 72)
    print(f"Finished     : {finished_at.isoformat(timespec='seconds')}")
    print(f"Elapsed time : {elapsed:.2f} seconds")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())