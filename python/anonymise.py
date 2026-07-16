"""Create the pseudonymised research dataset from the source dataset."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from python.schema import (
    load_research_schema,
    release_output_file,
    source_file,
)

from python.audit import (
    build_audit_record,
    write_audit_record,
)

DEFAULT_RANDOM_SEED = 33130


class AnonymisationError(ValueError):
    """Raised when the research dataset cannot be prepared safely."""


def validate_source_columns(
    dataframe: pd.DataFrame,
    schema: dict[str, Any],
) -> None:
    """Confirm that every schema column exists in the source dataset."""

    required_columns = list(schema["columns"].keys())

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        missing = ", ".join(missing_columns)

        raise AnonymisationError(
            "The source dataset is missing required columns: "
            f"{missing}"
        )


def generate_randomised_identifiers(
    row_count: int,
    identifier_format: str,
    random_generator: np.random.Generator,
) -> list[str]:
    """
    Generate randomly assigned identifiers.

    For example:

        R000001
        R000002
        R000003

    The identifier values are sequential, but their assignment to
    students is randomised.
    """

    numbers = np.arange(1, row_count + 1)

    random_generator.shuffle(numbers)

    return [
        identifier_format.format(number=int(number))
        for number in numbers
    ]


def build_research_dataset(
    source_dataframe: pd.DataFrame,
    schema: dict[str, Any],
    random_seed: int = DEFAULT_RANDOM_SEED,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Build the pseudonymised research dataset and restricted crosswalk.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        The research dataset and restricted student crosswalk.
    """

    validate_source_columns(source_dataframe, schema)

    dataframe = source_dataframe.copy()

    random_generator = np.random.default_rng(random_seed)

    source_identifier = schema["identifiers"]["source_identifier"]
    research_identifier = schema["identifiers"]["research_identifier"]

    source_id_column = source_identifier["column"]
    research_id_column = research_identifier["column"]
    research_id_format = research_identifier["format"]

    if dataframe[source_id_column].isna().any():
        raise AnonymisationError(
            f"Source identifier column '{source_id_column}' "
            "contains missing values."
        )

    if dataframe[source_id_column].duplicated().any():
        duplicated_count = int(
            dataframe[source_id_column].duplicated().sum()
        )

        raise AnonymisationError(
            f"Source identifier column '{source_id_column}' "
            f"contains {duplicated_count} duplicate values."
        )

    dataframe[research_id_column] = generate_randomised_identifiers(
        row_count=len(dataframe),
        identifier_format=research_id_format,
        random_generator=random_generator,
    )

    crosswalk = dataframe[
        [
            source_id_column,
            research_id_column,
        ]
    ].copy()

    output_columns: dict[str, pd.Series] = {}

    for source_column, column_rules in schema["columns"].items():
        research_action = column_rules["research_action"]

        if research_action == "remove":
            continue

        if research_action == "replace":
            continue

        if research_action == "retain":
            research_name = column_rules.get(
                "research_name",
                source_column,
            )

            output_columns[research_name] = dataframe[source_column]

            continue

        raise AnonymisationError(
            f"Unsupported research action '{research_action}' "
            f"for column '{source_column}'."
        )

    research_dataframe = pd.DataFrame(output_columns)

    research_dataframe.insert(
        0,
        research_id_column,
        dataframe[research_id_column],
    )

    if schema["processing"].get("shuffle_output_rows", False):
        research_dataframe = research_dataframe.sample(
            frac=1,
            random_state=random_seed,
        ).reset_index(drop=True)

    if len(research_dataframe) != len(source_dataframe):
        raise AnonymisationError(
            "Research dataset row count does not match "
            "the source dataset row count."
        )

    if research_dataframe[research_id_column].duplicated().any():
        raise AnonymisationError(
            "The generated research identifiers are not unique."
        )

    return research_dataframe, crosswalk


def prepare_research_release(
    schema_path: str | Path = "schema/research_schema.yaml",
    random_seed: int = DEFAULT_RANDOM_SEED,
) -> tuple[Path, Path, Path]:
    """
    Read the source CSV and write the research dataset,
    restricted crosswalk, and audit record.

    Returns
    -------
    tuple[Path, Path, Path]
        Paths to the research dataset, restricted crosswalk,
        and audit record.
    """

    schema = load_research_schema(schema_path)

    input_path = source_file(schema)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Source dataset not found: {input_path.resolve()}"
        )

    source_dataframe = pd.read_csv(input_path)

    research_dataframe, crosswalk = build_research_dataset(
        source_dataframe=source_dataframe,
        schema=schema,
        random_seed=random_seed,
    )

    research_output_path = release_output_file(
        schema,
        "research",
    )

    crosswalk_output_path = Path(
        schema["crosswalk"]["output_file"]
    )

    audit_output_path = Path(
        schema["audit"]["output_file"]
    )

    research_output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    crosswalk_output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    research_dataframe.to_csv(
        research_output_path,
        index=False,
    )

    crosswalk.to_csv(
        crosswalk_output_path,
        index=False,
    )

    removed_columns = [
        column_name
        for column_name, rules in schema["columns"].items()
        if rules["research_action"] in {"remove", "replace"}
    ]

    renamed_columns = {
        column_name: rules["research_name"]
        for column_name, rules in schema["columns"].items()
        if (
            rules["research_action"] == "retain"
            and rules.get("research_name", column_name)
            != column_name
        )
    }

    audit_record = build_audit_record(
        schema=schema,
        source_file=input_path,
        source_row_count=len(source_dataframe),
        output_row_count=len(research_dataframe),
        removed_columns=removed_columns,
        renamed_columns=renamed_columns,
        generalised_columns=[],
        suppressed_values={},
        random_seed=random_seed,
    )

    write_audit_record(
        record=audit_record,
        output_path=audit_output_path,
    )

    return (
        research_output_path,
        crosswalk_output_path,
        audit_output_path,
    )

def main() -> None:
    (
        research_path,
        crosswalk_path,
        audit_path,
    ) = prepare_research_release()

    print("Research data preparation completed.")
    print(f"Research dataset:      {research_path}")
    print(f"Restricted crosswalk:  {crosswalk_path}")
    print(f"Audit record:          {audit_path}")

if __name__ == "__main__":
    main()