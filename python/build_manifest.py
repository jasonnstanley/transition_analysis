"""Write a reproducibility build manifest."""

from __future__ import annotations

import json
import platform
import subprocess
from datetime import datetime
from pathlib import Path

from python.tools import find_git

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def get_git_commit() -> str:
    """Return the current Git commit hash."""

    git = find_git()

    result = subprocess.run(
        [str(git), "rev-parse", "HEAD"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout.strip()


def write_manifest() -> None:
    """Write the current build manifest."""

    manifest = {
        "toolkit": "Transition Analysis Toolkit",
        "build_time": datetime.now().isoformat(timespec="seconds"),
        "git_commit": get_git_commit(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "status": "SUCCESS",
    }

    output = PROJECT_ROOT / "logs" / "build_manifest.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    output.write_text(
        json.dumps(manifest, indent=4),
        encoding="utf-8",
    )

    print(f"Manifest written: {output}")


def main() -> None:
    write_manifest()


if __name__ == "__main__":
    main()