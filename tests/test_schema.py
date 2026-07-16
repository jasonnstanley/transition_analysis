"""Verify that the research dataset matches the published YAML schema."""

from pathlib import Path

import pandas as pd
import yaml


SCHEMA_PATH = Path("schema/research_schema.yaml")
DATA_PATH = Path("data/processed/transition_research.csv")


def extract_expected_research_columns(schema: dict) -> list[str]:
    """Return the ordered research-release column names from the schema."""

    identifiers = schema.get("identifiers", {})
    columns = schema.get("columns", {})

    expected = []

    research_identifier = identifiers.get("research_identifier", {})
    identifier_name = research_identifier.get("column")

    if identifier_name:
        expected.append(identifier_name)

    for source_name, definition in columns.items():
        if not isinstance(definition, dict):
            raise TypeError(
                f"Schema entry for {source_name!r} must be a mapping."
            )

        research_action = definition.get("research_action")

        if research_action == "remove":
            continue

        if research_action == "replace":
            continue

        research_name = definition.get("research_name")

        if research_name:
            expected.append(research_name)

    return expected


def main() -> None:
    """Compare processed research columns with the authoritative schema."""

    assert SCHEMA_PATH.exists(), f"Missing schema: {SCHEMA_PATH}"
    assert DATA_PATH.exists(), f"Missing dataset: {DATA_PATH}"

    with SCHEMA_PATH.open("r", encoding="utf-8") as file:
        schema = yaml.safe_load(file)

    expected = extract_expected_research_columns(schema)

    data = pd.read_csv(DATA_PATH)
    actual = list(data.columns)

    assert expected == actual, (
        "\nResearch schema mismatch.\n"
        f"\nExpected columns ({len(expected)}):\n{expected}"
        f"\n\nActual columns ({len(actual)}):\n{actual}\n"
    )

    print("Research schema verified.")
    print(f"{len(actual)} columns checked.")


if __name__ == "__main__":
    main()