"""Load and perform structural checks on the research schema."""

from pathlib import Path
from typing import Any

import yaml


DEFAULT_SCHEMA_PATH = Path("schema/research_schema.yaml")


class SchemaError(ValueError):
    """Raised when the research schema is missing or structurally invalid."""


def load_research_schema(
    schema_path: str | Path = DEFAULT_SCHEMA_PATH,
) -> dict[str, Any]:
    """
    Load the authoritative research schema.

    Parameters
    ----------
    schema_path:
        Path to the YAML research schema.

    Returns
    -------
    dict[str, Any]
        Parsed research schema.

    Raises
    ------
    FileNotFoundError
        If the schema file does not exist.
    SchemaError
        If the YAML is empty or structurally invalid.
    """
    path = Path(schema_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Research schema not found: {path.resolve()}"
        )

    with path.open("r", encoding="utf-8") as schema_file:
        schema = yaml.safe_load(schema_file)

    if not isinstance(schema, dict):
        raise SchemaError(
            "The research schema must contain a top-level YAML mapping."
        )

    validate_schema_structure(schema)

    return schema


def validate_schema_structure(schema: dict[str, Any]) -> None:
    """
    Validate the required top-level structure of the schema.

    This is an initial structural validation only. Detailed validation
    of individual column rules will be added separately.
    """
    required_sections = {
        "schema",
        "source",
        "identifiers",
        "crosswalk",
        "release_levels",
        "columns",
        "privacy_review",
        "processing",
        "audit",
    }

    missing_sections = required_sections.difference(schema)

    if missing_sections:
        missing = ", ".join(sorted(missing_sections))
        raise SchemaError(
            f"Research schema is missing required sections: {missing}"
        )

    schema_metadata = schema["schema"]

    if not isinstance(schema_metadata, dict):
        raise SchemaError(
            "The 'schema' section must be a YAML mapping."
        )

    required_metadata = {
        "name",
        "version",
        "description",
    }

    missing_metadata = required_metadata.difference(schema_metadata)

    if missing_metadata:
        missing = ", ".join(sorted(missing_metadata))
        raise SchemaError(
            f"Schema metadata is missing required fields: {missing}"
        )

    release_levels = schema["release_levels"]

    if not isinstance(release_levels, dict):
        raise SchemaError(
            "The 'release_levels' section must be a YAML mapping."
        )

    required_release_levels = {
        "internal",
        "research",
        "public",
    }

    missing_release_levels = required_release_levels.difference(
        release_levels
    )

    if missing_release_levels:
        missing = ", ".join(sorted(missing_release_levels))
        raise SchemaError(
            f"Missing release levels: {missing}"
        )

    columns = schema["columns"]

    if not isinstance(columns, dict) or not columns:
        raise SchemaError(
            "The 'columns' section must contain at least one column."
        )


def schema_version(schema: dict[str, Any]) -> str:
    """Return the schema version."""
    return str(schema["schema"]["version"])


def source_file(schema: dict[str, Any]) -> Path:
    """Return the source dataset path recorded in the schema."""
    return Path(schema["source"]["input_file"])


def release_output_file(
    schema: dict[str, Any],
    release_level: str,
) -> Path:
    """
    Return the output path for a release level.

    Parameters
    ----------
    schema:
        Loaded research schema.
    release_level:
        One of ``internal``, ``research``, or ``public``.
    """
    release_levels = schema["release_levels"]

    if release_level not in release_levels:
        valid = ", ".join(release_levels)
        raise SchemaError(
            f"Unknown release level '{release_level}'. "
            f"Expected one of: {valid}"
        )

    return Path(release_levels[release_level]["output_file"])