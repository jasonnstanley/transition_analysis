"""Feature-importance reporting for tree-based models."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from python.tree_tuning import TunedTreeResult


DEFAULT_REPORT_DATA_DIRECTORY = Path("reports/data")
DEFAULT_REPORT_TABLE_DIRECTORY = Path("reports/tables")

DEFAULT_TUNED_IMPORTANCE_LONG = (
    DEFAULT_REPORT_DATA_DIRECTORY
    / "tuned_feature_importance_long.csv"
)

DEFAULT_TUNED_IMPORTANCE_WIDE = (
    DEFAULT_REPORT_DATA_DIRECTORY
    / "tuned_feature_importance_wide.csv"
)

DEFAULT_TUNED_IMPORTANCE_TEX = (
    DEFAULT_REPORT_TABLE_DIRECTORY
    / "tuned_feature_importance.tex"
)

def tuned_model_label(
    tuned_result: TunedTreeResult,
) -> str:
    """Return a concise label for a tuned model."""

    result = tuned_result.result

    risk_label = (
        "With Risk"
        if result.dataset_name == "With Risk Index"
        else "Without Risk"
    )

    if result.model_name == "Tuned Decision Tree":
        model_label = "Decision Tree"
    elif result.model_name == "Tuned Random Forest":
        model_label = "Random Forest"
    else:
        model_label = result.model_name

    return f"{model_label} — {risk_label}"


def build_tuned_importance_long(
    tuned_results: list[TunedTreeResult],
) -> pd.DataFrame:
    """
    Build a long-format feature-importance table.

    The output has one row per feature per model.
    """

    frames: list[pd.DataFrame] = []

    for tuned_result in tuned_results:
        result = tuned_result.result

        importance = result.feature_importance.copy()

        importance.insert(
            0,
            "model",
            tuned_model_label(tuned_result),
        )

        importance.insert(
            1,
            "model_type",
            result.model_name,
        )

        importance.insert(
            2,
            "dataset",
            result.dataset_name,
        )

        importance.insert(
            3,
            "rank",
            range(1, len(importance) + 1),
        )

        frames.append(importance)

    long_table = pd.concat(
        frames,
        ignore_index=True,
    )

    return long_table[
        [
            "model",
            "model_type",
            "dataset",
            "rank",
            "feature",
            "importance",
        ]
    ]


def build_tuned_importance_wide(
    long_table: pd.DataFrame,
) -> pd.DataFrame:
    """
    Pivot the long-format table into one column per model.
    """

    wide_table = long_table.pivot_table(
        index="feature",
        columns="model",
        values="importance",
        aggfunc="first",
        fill_value=0.0,
    )

    wide_table = wide_table.reset_index()

    model_columns = [
        column
        for column in wide_table.columns
        if column != "feature"
    ]

    wide_table["mean_importance"] = wide_table[
        model_columns
    ].mean(axis=1)

    wide_table["maximum_importance"] = wide_table[
        model_columns
    ].max(axis=1)

    wide_table = wide_table.sort_values(
        by=[
            "mean_importance",
            "maximum_importance",
        ],
        ascending=False,
    ).reset_index(drop=True)

    return wide_table


def write_importance_long(
    dataframe: pd.DataFrame,
    output_path: str | Path = DEFAULT_TUNED_IMPORTANCE_LONG,
) -> Path:
    """Write long-format feature importances to CSV."""

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_csv(
        path,
        index=False,
    )

    return path


def write_importance_wide(
    dataframe: pd.DataFrame,
    output_path: str | Path = DEFAULT_TUNED_IMPORTANCE_WIDE,
) -> Path:
    """Write wide-format feature importances to CSV."""

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_csv(
        path,
        index=False,
    )

    return path


def write_importance_latex(
    dataframe: pd.DataFrame,
    output_path: str | Path = DEFAULT_TUNED_IMPORTANCE_TEX,
    top_n: int = 12,
) -> Path:
    """Write the highest-ranked features as a LaTeX table."""

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    latex_table = dataframe.head(top_n).copy()

    latex_table = latex_table.rename(
        columns={
            "feature": "Feature",
            "Decision Tree — Without Risk": "DT Without Risk",
            "Decision Tree — With Risk": "DT With Risk",
            "Random Forest — Without Risk": "RF Without Risk",
            "Random Forest — With Risk": "RF With Risk",
            "mean_importance": "Mean",
            "maximum_importance": "Maximum",
        }
    )

    latex = latex_table.to_latex(
        index=False,
        float_format="%.4f",
        caption=(
            "Feature importance comparison for the "
            "cross-validated tree-based models."
        ),
        label="tab:tuned_feature_importance",
        position="htbp",
        escape=True,
    )

    path.write_text(
        latex,
        encoding="utf-8",
    )

    return path


def write_tuned_feature_reports(
    tuned_results: list[TunedTreeResult],
) -> tuple[Path, Path, Path]:
    """Generate all tuned feature-importance reports."""

    long_table = build_tuned_importance_long(
        tuned_results
    )

    wide_table = build_tuned_importance_wide(
        long_table
    )

    long_path = write_importance_long(
        long_table
    )

    wide_path = write_importance_wide(
        wide_table
    )

    latex_path = write_importance_latex(
        wide_table
    )

    return long_path, wide_path, latex_path


def print_tuned_importance_summary(
    tuned_results: list[TunedTreeResult],
    top_n: int = 5,
) -> None:
    """Print the leading features for each tuned model."""

    long_table = build_tuned_importance_long(
        tuned_results
    )

    print()
    print("=" * 96)
    print("Tuned Feature-Importance Summary")
    print("=" * 96)

    for model_name in long_table["model"].unique():
        model_rows = long_table[
            long_table["model"] == model_name
        ].head(top_n)

        print()
        print(model_name)
        print("-" * 72)

        print(
            model_rows[
                [
                    "rank",
                    "feature",
                    "importance",
                ]
            ].to_string(
                index=False,
                formatters={
                    "importance": (
                        lambda value: f"{value:.4f}"
                    ),
                },
            )
        )