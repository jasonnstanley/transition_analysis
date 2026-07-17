"""Build logging utilities."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_ROOT / "logs"


def log(message: str) -> None:
    """Append a timestamped message to the build log."""
    LOG_DIR.mkdir(exist_ok=True)

    logfile = LOG_DIR / "build.log"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with logfile.open("a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] {message}\n")