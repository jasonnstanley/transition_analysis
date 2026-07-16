"""Generate data dictionaries from the authoritative research schema."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from python.schema import load_research_schema


DEFAULT_MARKDOWN_OUTPUT = Path("docs/research_data_dictionary.md")
DEFAULT_CSV_OUTPUT = Path("docs/research_data_dictionary.csv")


def _escape_markdown(value: Any) -> str:
    """Convert a value to safe Markdown table text."""

    if value is None:
        return ""

    return str(value).replace("|", r"\|").replace("\n", " ")


def build_dictionary_rows(
    schema: dict[str, Any],
    release_level: str = "research",
) -> list[dict[str, str]]:
    """
    Build data-dictionary rows for a selected release level.

    Parameters
    ----------
    schema:
        Loaded research schema.
    release_level:
        Either ``internal``, ``research``, or ``public``.

    Returns
    -------
    list[dict[str, str]]
        Structured data-dictionary rows.
    """

    valid_levels = {
        "internal",
        "research",
        "public",
    }

    if release_level not in valid_levels:
        valid = ", ".join(sorted(valid_levels))

        raise ValueError(
            f"Unknown release level '{release_level}'. "
            f"Expected one of: {valid}"
        )

    action_key = f"{release_level}_action"
    name_key = f"{release_level}_name"

    rows: list[dict[str, str]] = []

    if release_level == "research":
        research_identifier = schema["identifiers"][
            "research_identifier"
        ]

        rows.append(
            {
                "source_column": schema["identifiers"][
                    "source_identifier"
                ]["column"],
                "release_column": research_identifier["column"],
                "classification": "pseudonymous_identifier",
                "action": "replace",
                "description": (
                    "Randomly assigned research identifier replacing "
                    "the institutional student identifier."
                ),
            }
        )

    if release_level == "public":
        public_identifier = schema["identifiers"][
            "public_identifier"
        ]

        rows.append(
            {
                "source_column": "",
                "release_column": public_identifier["column"],
                "classification": "deidentified_identifier",
                "action": "create",
                "description": (
                    "Randomly assigned public identifier with no "
                    "retained crosswalk."
                ),
            }
        )

    for source_column, rules in schema["columns"].items():
        action = str(rules[action_key])

        # Replacement identifiers are already documented by the
        # generated research_id or public_id row above.
        if action == "replace":
            continue

        if action == "remove":
            release_column = ""
        else:
            release_column = str(
                rules.get(
                    name_key,
                    source_column,
                )
            )
        
        rows.append(
            {
                "source_column": source_column,
                "release_column": release_column,
                "classification": str(
                    rules.get("classification", "")
                ),
                "action": action,
                "description": str(
                    rules.get("description", "")
                ),
            }
        )

    return rows


def write_markdown_dictionary(
    *,
    schema: dict[str, Any],
    rows: list[dict[str, str]],
    release_level: str,
    output_path: str | Path,
) -> Path:
    """Write a Markdown data dictionary."""

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    schema_name = schema["schema"]["name"]
    schema_version = schema["schema"]["version"]
    release_description = schema["release_levels"][
        release_level
    ]["description"].strip()

    lines = [
        "# Transition Analysis Data Dictionary",
        "",
        f"**Schema:** `{schema_name}`  ",
        f"**Schema version:** `{schema_version}`  ",
        f"**Release level:** `{release_level}`",
        "",
        release_description,
        "",
        "| Source column | Release column | Classification | Action | Description |",
        "|---|---|---|---|---|",
    ]

    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_markdown(row["source_column"]),
                    _escape_markdown(row["release_column"]),
                    _escape_markdown(row["classification"]),
                    _escape_markdown(row["action"]),
                    _escape_markdown(row["description"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Privacy controls",
            "",
            (
                f"- Minimum group size: "
                f"{schema['privacy_review']['minimum_group_size']}"
            ),
            (
                "- Columns requiring public-release review: "
                + ", ".join(
                    schema["privacy_review"]["review_columns"]
                )
            ),
            "",
            (
                "This file is generated from "
                "`schema/research_schema.yaml`. "
                "Do not edit it manually."
            ),
            "",
        ]
    )

    path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return path


def write_csv_dictionary(
    *,
    rows: list[dict[str, str]],
    output_path: str | Path,
) -> Path:
    """Write a CSV data dictionary."""

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "source_column",
        "release_column",
        "classification",
        "action",
        "description",
    ]

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)

    return path


def generate_data_dictionary(
    schema_path: str | Path = "schema/research_schema.yaml",
    release_level: str = "research",
    markdown_output: str | Path = DEFAULT_MARKDOWN_OUTPUT,
    csv_output: str | Path = DEFAULT_CSV_OUTPUT,
) -> tuple[Path, Path]:
    """Generate Markdown and CSV data dictionaries."""

    schema = load_research_schema(schema_path)

    rows = build_dictionary_rows(
        schema=schema,
        release_level=release_level,
    )

    markdown_path = write_markdown_dictionary(
        schema=schema,
        rows=rows,
        release_level=release_level,
        output_path=markdown_output,
    )

    csv_path = write_csv_dictionary(
        rows=rows,
        output_path=csv_output,
    )

    return markdown_path, csv_path


def main() -> None:
    markdown_path, csv_path = generate_data_dictionary()

    print("Research data dictionary generated.")
    print(f"Markdown: {markdown_path}")
    print(f"CSV:      {csv_path}")


if __name__ == "__main__":
    main()