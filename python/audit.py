"""Audit-record support for research data preparation."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class AuditError(ValueError):
    """Raised when an audit record cannot be created safely."""


def build_audit_record(
    *,
    schema: dict[str, Any],
    source_file: Path,
    source_row_count: int,
    output_row_count: int,
    removed_columns: list[str],
    renamed_columns: dict[str, str],
    generalised_columns: list[str],
    suppressed_values: dict[str, int],
    random_seed: int,
) -> dict[str, Any]:
    """Build the data-preparation audit record."""

    record = {
        "schema_version": str(schema["schema"]["version"]),
        "source_file": str(source_file),
        "source_row_count": int(source_row_count),
        "output_row_count": int(output_row_count),
        "removed_columns": removed_columns,
        "renamed_columns": renamed_columns,
        "generalised_columns": generalised_columns,
        "suppressed_values": suppressed_values,
        "random_seed": int(random_seed),
        "execution_timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    required_fields = schema["audit"]["include"]

    missing_fields = [
        field
        for field in required_fields
        if field not in record
    ]

    if missing_fields:
        missing = ", ".join(missing_fields)

        raise AuditError(
            f"Audit record is missing required fields: {missing}"
        )

    return record


def write_audit_record(
    record: dict[str, Any],
    output_path: str | Path,
) -> Path:
    """Write an audit record as formatted JSON."""

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open("w", encoding="utf-8") as audit_file:
        json.dump(
            record,
            audit_file,
            indent=2,
            ensure_ascii=False,
        )

        audit_file.write("\n")

    return path