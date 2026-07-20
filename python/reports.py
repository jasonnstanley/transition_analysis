"""Build all canonical research reports."""

from __future__ import annotations

import subprocess
import sys


def run_report(name: str, module: str) -> None:
    """Run one report-generation module."""

    command = [sys.executable, "-m", module]

    print()
    print("-" * 72)
    print(name)
    print("-" * 72)
    print(f"Command: {' '.join(command)}")
    print()

    result = subprocess.run(command, check=False)

    if result.returncode != 0:
        raise RuntimeError(
            f"{name} failed with exit code {result.returncode}"
        )

    print()
    print(f"✓ {name}")


def main() -> None:
    """Build all canonical research reports."""

    print("Building canonical research reports...")

    run_report(
        "Grouped and individual feature-importance reports",
        "python.interpret_models",
    )

    print()
    print("✓ Canonical research reports built successfully")


if __name__ == "__main__":
    main()