"""Audit records for reproducible analysis and modelling runs."""

from __future__ import annotations

import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any


class AnalysisAuditError(ValueError):
    """Raised when an analysis audit record is invalid."""


class AnalysisTimer:
    """Simple timer for recording total analysis duration."""

    def __init__(self) -> None:
        self._start_time: float | None = None
        self._end_time: float | None = None

    def start(self) -> None:
        """Start the timer."""

        self._start_time = perf_counter()
        self._end_time = None

    def stop(self) -> float:
        """Stop the timer and return elapsed seconds."""

        if self._start_time is None:
            raise AnalysisAuditError(
                "The analysis timer has not been started."
            )

        self._end_time = perf_counter()

        return self.elapsed_seconds

    @property
    def elapsed_seconds(self) -> float:
        """Return elapsed time in seconds."""

        if self._start_time is None:
            raise AnalysisAuditError(
                "The analysis timer has not been started."
            )

        endpoint = (
            self._end_time
            if self._end_time is not None
            else perf_counter()
        )

        return endpoint - self._start_time


def build_analysis_audit(
    *,
    schema: dict[str, Any],
    analysis_name: str,
    dataset_path: str | Path,
    dataset_rows: int,
    dataset_columns: int,
    random_seed: int,
    test_size: float,
    training_rows: int,
    test_rows: int,
    cv_folds: int | None,
    selection_metric: str | None,
    models: list[dict[str, Any]],
    output_files: list[str | Path],
    execution_seconds: float,
) -> dict[str, Any]:
    """Build a formal modelling audit record."""

    if dataset_rows <= 0:
        raise AnalysisAuditError(
            "Dataset row count must be positive."
        )

    if training_rows + test_rows != dataset_rows:
        raise AnalysisAuditError(
            "Training and test row counts do not equal "
            "the full dataset row count."
        )

    audit = {
        "analysis_name": analysis_name,
        "schema_name": schema["schema"]["name"],
        "schema_version": str(
            schema["schema"]["version"]
        ),
        "dataset": str(dataset_path),
        "dataset_rows": int(dataset_rows),
        "dataset_columns": int(dataset_columns),
        "random_seed": int(random_seed),
        "test_size": float(test_size),
        "training_rows": int(training_rows),
        "test_rows": int(test_rows),
        "cross_validation_folds": (
            int(cv_folds)
            if cv_folds is not None
            else None
        ),
        "selection_metric": selection_metric,
        "models": models,
        "output_files": [
            str(path)
            for path in output_files
        ],
        "environment": {
            "python_version": platform.python_version(),
            "python_executable": sys.executable,
            "operating_system": platform.system(),
            "platform": platform.platform(),
        },
        "execution_seconds": round(
            float(execution_seconds),
            6,
        ),
        "execution_timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    return audit


def write_analysis_audit(
    audit: dict[str, Any],
    output_path: str | Path,
) -> Path:
    """Write a formatted JSON analysis audit."""

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            audit,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    return path