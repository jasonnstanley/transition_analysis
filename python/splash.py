"""Console splash screen for the Transition Analysis Toolkit."""

from __future__ import annotations

import platform
import sys
from pathlib import Path
from typing import Any

from python.schema import (
    release_output_file,
    schema_version,
    source_file,
)


TOOLKIT_NAME = "Transition Analysis Toolkit"
TOOLKIT_VERSION = "0.3.0"
LINE_WIDTH = 72


def _line(character: str = "=") -> str:
    """Return a horizontal divider."""

    return character * LINE_WIDTH


def _status_line(message: str, passed: bool = True) -> str:
    """Return a formatted status line."""

    symbol = "[OK]" if passed else "[FAIL]"

    return f"{symbol:<7} {message}"


def _path_status(path: Path) -> tuple[str, bool]:
    """Return a readable path status."""

    exists = path.exists()

    if exists:
        return f"{path} found", True

    return f"{path} not found", False


def print_banner() -> None:
    """Print the toolkit heading."""

    print(_line())
    print(TOOLKIT_NAME)
    print(_line())


def print_environment() -> None:
    """Print Python and platform information."""

    print()
    print(f"{'Toolkit Version':<20}: {TOOLKIT_VERSION}")
    print(f"{'Python':<20}: {platform.python_version()}")
    print(f"{'Platform':<20}: {platform.system()}")
    print(f"{'Executable':<20}: {sys.executable}")


def print_schema_information(
    schema: dict[str, Any],
) -> None:
    """Print schema and dataset path information."""

    schema_name = schema["schema"]["name"]
    schema_path = Path("schema/research_schema.yaml")
    input_path = source_file(schema)
    research_path = release_output_file(schema, "research")
    public_path = release_output_file(schema, "public")
    crosswalk_path = Path(schema["crosswalk"]["output_file"])

    print()
    print(f"{'Research Schema':<20}: {schema_name}")
    print(f"{'Schema Version':<20}: {schema_version(schema)}")
    print(f"{'Schema File':<20}: {schema_path}")
    print()
    print(f"{'Source Dataset':<20}: {input_path}")
    print(f"{'Research Dataset':<20}: {research_path}")
    print(f"{'Public Dataset':<20}: {public_path}")
    print(f"{'Crosswalk':<20}: {crosswalk_path}")


def print_pipeline_status(
    schema: dict[str, Any],
) -> bool:
    """
    Print file and configuration checks.

    Returns
    -------
    bool
        True when all required startup checks pass.
    """

    schema_path = Path("schema/research_schema.yaml")
    input_path = source_file(schema)
    research_path = release_output_file(schema, "research")
    crosswalk_path = Path(schema["crosswalk"]["output_file"])

    checks = [
        ("Research schema loaded", True),
        _path_status(schema_path),
        _path_status(input_path),
        _path_status(research_path),
        _path_status(crosswalk_path),
    ]

    print()
    print("Status")
    print(_line("-"))

    all_passed = True

    for message, passed in checks:
        print(_status_line(message, passed))

        if not passed:
            all_passed = False

    return all_passed


def print_dataset_summary(
    dataframe: Any,
    identifier_column: str | None = None,
) -> None:
    """
    Print a summary of a loaded pandas DataFrame.

    The type is intentionally general so splash.py does not need
    to import pandas directly.
    """

    rows = len(dataframe)
    columns = len(dataframe.columns)

    print()
    print("Dataset Summary")
    print(_line("-"))
    print(f"{'Rows':<20}: {rows:,}")
    print(f"{'Columns':<20}: {columns}")

    if identifier_column is not None:
        if identifier_column in dataframe.columns:
            unique_ids = dataframe[identifier_column].nunique(
                dropna=False
            )

            duplicated_ids = int(
                dataframe[identifier_column].duplicated().sum()
            )

            print(f"{'Identifier':<20}: {identifier_column}")
            print(f"{'Unique IDs':<20}: {unique_ids:,}")
            print(f"{'Duplicate IDs':<20}: {duplicated_ids}")
        else:
            print(
                f"{'Identifier':<20}: "
                f"{identifier_column} not found"
            )


def print_ready(pipeline_ready: bool = True) -> None:
    """Print the final startup message."""

    print()

    if pipeline_ready:
        print(_line())
        print("Ready for Analysis")
        print(_line())
    else:
        print(_line("!"))
        print("Startup checks require attention")
        print(_line("!"))


def splash(
    schema: dict[str, Any],
    dataframe: Any | None = None,
    identifier_column: str | None = None,
) -> bool:
    """
    Print the complete toolkit splash screen.

    Parameters
    ----------
    schema:
        Loaded research schema.
    dataframe:
        Optional loaded dataset.
    identifier_column:
        Optional identifier column used for dataset checks.

    Returns
    -------
    bool
        True when all startup checks pass.
    """

    print_banner()
    print_environment()
    print_schema_information(schema)

    pipeline_ready = print_pipeline_status(schema)

    if dataframe is not None:
        print_dataset_summary(
            dataframe=dataframe,
            identifier_column=identifier_column,
        )

    print_ready(pipeline_ready)

    return pipeline_ready