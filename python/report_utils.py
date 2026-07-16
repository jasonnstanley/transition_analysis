"""
Shared report-export utilities for the Transition Analysis Toolkit.
"""

from pathlib import Path

import pandas as pd


def validate_columns(
    df: pd.DataFrame,
    required_columns: set[str],
    context: str = "Dataframe",
) -> None:
    """
    Confirm that a dataframe contains all required columns.

    Parameters
    ----------
    df:
        Dataframe to validate.

    required_columns:
        Column names required by the analysis.

    context:
        Human-readable description used in error messages.
    """

    missing_columns = required_columns.difference(df.columns)

    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))

        raise ValueError(
            f"{context} is missing required columns: {missing_text}"
        )


def save_dataframe_reports(
    df: pd.DataFrame,
    output_directory: Path,
    csv_name: str,
    tex_name: str,
    float_format: str = "%.4f",
    latex_caption: str | None = None,
    latex_label: str | None = None,
) -> tuple[Path, Path]:
    """
    Save a dataframe in CSV and LaTeX formats.

    Returns
    -------
    tuple[Path, Path]
        Paths to the CSV and LaTeX files.
    """

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    csv_path = output_directory / csv_name
    tex_path = output_directory / tex_name

    df.to_csv(
        csv_path,
        index=False,
    )

    latex = df.to_latex(
        index=False,
        float_format=float_format,
        escape=True,
        caption=latex_caption,
        label=latex_label,
    )

    tex_path.write_text(
        latex,
        encoding="utf-8",
    )

    return csv_path, tex_path