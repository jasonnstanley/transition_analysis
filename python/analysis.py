"""Run the canonical Python research analysis."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_analysis(name: str, module: str) -> None:
    """Run one canonical analysis module."""

    command = [sys.executable, "-m", module]

    print()
    print("-" * 72)
    print(name)
    print("-" * 72)
    print(f"Command: {' '.join(command)}")
    print()

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"{name} failed with exit code {result.returncode}"
        )

    print()
    print(f"✓ {name}")

def main() -> None:
    """Run all canonical Python analyses."""

    print("Running canonical Python analysis...")

    run_analysis(
        "Core statistical and classification analysis",
        "python.run_models",
    )

    print()
    print("✓ Canonical Python analysis completed successfully")


if __name__ == "__main__":
    main()