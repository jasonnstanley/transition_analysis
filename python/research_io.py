"""Load and validate the pseudonymised research dataset."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from python.schema import (
    load_research_schema,
    release_output_file,
)


class ResearchDataError(ValueError):
    """Raised when the research dataset fails validation."""


def expected_research_columns(
    schema: dict[str, Any],
) -> list[str]:
    """
    Return the columns expected in the research dataset.

    The list is generated entirely from the authoritative schema.
    """

    research_id_column = schema[
        "identifiers"
    ][
        "research_identifier"
    ][
        "column"
    ]

    columns = [research_id_column]

    for source_column, rules in schema["columns"].items():
        action = rules["research_action"]

        if action in {"remove", "replace"}:
            continue

        if action == "retain":
            research_name = rules.get(
                "research_name",
                source_column,
            )

            columns.append(research_name)
            continue

        raise ResearchDataError(
            f"Unsupported research action '{action}' "
            f"for column '{source_column}'."
        )

    return columns


def validate_research_dataset(
    dataframe: pd.DataFrame,
    schema: dict[str, Any],
) -> None:
    """Validate the structure and identifiers of a research dataset."""

    expected_columns = expected_research_columns(schema)
    actual_columns = list(dataframe.columns)

    missing_columns = [
        column
        for column in expected_columns
        if column not in actual_columns
    ]

    unexpected_columns = [
        column
        for column in actual_columns
        if column not in expected_columns
    ]

    if missing_columns:
        missing = ", ".join(missing_columns)

        raise ResearchDataError(
            f"Research dataset is missing columns: {missing}"
        )

    if unexpected_columns:
        unexpected = ", ".join(unexpected_columns)

        raise ResearchDataError(
            f"Research dataset contains unexpected columns: "
            f"{unexpected}"
        )

    research_id_column = schema[
        "identifiers"
    ][
        "research_identifier"
    ][
        "column"
    ]

    if dataframe[research_id_column].isna().any():
        raise ResearchDataError(
            f"Research identifier column '{research_id_column}' "
            "contains missing values."
        )

    duplicate_count = int(
        dataframe[research_id_column].duplicated().sum()
    )

    if duplicate_count:
        raise ResearchDataError(
            f"Research identifier column '{research_id_column}' "
            f"contains {duplicate_count} duplicate values."
        )

    direct_identifiers = [
        column_name
        for column_name, rules in schema["columns"].items()
        if rules["classification"] == "direct_identifier"
    ]

    retained_direct_identifiers = [
        column
        for column in direct_identifiers
        if column in dataframe.columns
    ]

    if retained_direct_identifiers:
        retained = ", ".join(retained_direct_identifiers)

        raise ResearchDataError(
            "Direct identifiers were found in the research dataset: "
            f"{retained}"
        )


def load_research_data(
    schema_path: str | Path = "schema/research_schema.yaml",
) -> pd.DataFrame:
    """
    Load and validate the pseudonymised research dataset.

    Returns
    -------
    pandas.DataFrame
        Validated research dataset.
    """

    schema = load_research_schema(schema_path)

    data_path = release_output_file(
        schema,
        "research",
    )

    if not data_path.exists():
        raise FileNotFoundError(
            f"Research dataset not found: {data_path.resolve()}\n"
            "Run `python -m python.anonymise` first."
        )

    dataframe = pd.read_csv(data_path)

    validate_research_dataset(
        dataframe=dataframe,
        schema=schema,
    )

    return dataframe