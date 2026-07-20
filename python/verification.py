"""Run the independent R verification suite."""

from __future__ import annotations


import subprocess
from pathlib import Path
from python.tools import find_rscript

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_r_verification(name: str, script: str) -> None:
    """Run one independent R verification script."""

    rscript = find_rscript()

    script_path = PROJECT_ROOT / script

    if not script_path.exists():
        raise FileNotFoundError(
            f"R verification script not found: {script_path}"
        )

    command = [str(rscript), str(script_path)]

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
    """Run all independent R verification scripts."""

    print("Running independent R verification...")

    run_r_verification(
        "Independent R verification — tuned tree models",
        "R/verify_tree_models.R",
    )

    print()
    print("✓ Independent R verification completed successfully")


if __name__ == "__main__":
    main()