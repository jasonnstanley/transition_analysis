"""Reporting utilities for baseline tree-model comparisons."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from python.tree_models import TreeModelResult


DEFAULT_REPORT_DATA_DIRECTORY = Path("reports/data")
DEFAULT_REPORT_TABLE_DIRECTORY = Path("reports/tables")

DEFAULT_COMPARISON_CSV = (
    DEFAULT_REPORT_DATA_DIRECTORY / "baseline_tree_models.csv"
)
DEFAULT_COMPARISON_TEX = (
    DEFAULT_REPORT_TABLE_DIRECTORY / "baseline_tree_models.tex"
)
DEFAULT_IMPORTANCE_CSV = (
    DEFAULT_REPORT_DATA_DIRECTORY / "baseline_feature_importance.csv"
)


def model_label(result: TreeModelResult) -> str:
    """Return a concise model label."""

    risk_label = (
        "With Risk Index"
        if result.dataset_name == "With Risk Index"
        else "Without Risk Index"
    )

    return f"{result.model_name} — {risk_label}"


def build_model_comparison(
    results: list[TreeModelResult],
) -> pd.DataFrame:
    """Build one comparison table from all model results."""

    rows: list[dict[str, object]] = []

    for result in results:
        metrics = result.metrics

        rows.append(
            {
                "model": model_label(result),
                "model_type": result.model_name,
                "dataset": result.dataset_name,
                "test_rows": metrics["test_rows"],
                "passes": metrics["passes"],
                "non_passes": metrics["non_passes"],
                "accuracy": metrics["accuracy"],
                "balanced_accuracy": metrics[
                    "balanced_accuracy"
                ],
                "precision": metrics["precision"],
                "recall": metrics["recall"],
                "f1": metrics["f1"],
                "roc_auc": metrics["roc_auc"],
            }
        )

    return pd.DataFrame(rows)


def build_feature_importance_report(
    results: list[TreeModelResult],
) -> pd.DataFrame:
    """
    Combine feature importances from all baseline tree models.

    The output uses long format, with one row per feature per model.
    """

    frames: list[pd.DataFrame] = []

    for result in results:
        importance = result.feature_importance.copy()

        importance.insert(
            0,
            "model",
            model_label(result),
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

    return pd.concat(
        frames,
        ignore_index=True,
    )


def write_comparison_csv(
    comparison: pd.DataFrame,
    output_path: str | Path = DEFAULT_COMPARISON_CSV,
) -> Path:
    """Write the baseline model comparison to CSV."""

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    comparison.to_csv(
        path,
        index=False,
    )

    return path


def write_feature_importance_csv(
    feature_importance: pd.DataFrame,
    output_path: str | Path = DEFAULT_IMPORTANCE_CSV,
) -> Path:
    """Write combined feature importances to CSV."""

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    feature_importance.to_csv(
        path,
        index=False,
    )

    return path


def write_comparison_latex(
    comparison: pd.DataFrame,
    output_path: str | Path = DEFAULT_COMPARISON_TEX,
) -> Path:
    """Write a publication-ready LaTeX comparison table."""

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    latex_table = comparison[
        [
            "model",
            "accuracy",
            "balanced_accuracy",
            "precision",
            "recall",
            "f1",
            "roc_auc",
        ]
    ].rename(
        columns={
            "model": "Model",
            "accuracy": "Accuracy",
            "balanced_accuracy": "Balanced Accuracy",
            "precision": "Precision",
            "recall": "Recall",
            "f1": "F1",
            "roc_auc": "ROC AUC",
        }
    )

    latex = latex_table.to_latex(
        index=False,
        float_format="%.4f",
        caption=(
            "Baseline Decision Tree and Random Forest "
            "performance on the held-out test dataset."
        ),
        label="tab:baseline_tree_models",
        position="htbp",
        escape=True,
    )

    path.write_text(
        latex,
        encoding="utf-8",
    )

    return path


def write_baseline_reports(
    results: list[TreeModelResult],
) -> tuple[Path, Path, Path]:
    """
    Generate all baseline tree-model reports.

    Returns
    -------
    tuple[Path, Path, Path]
        Comparison CSV, comparison LaTeX, and feature-importance CSV.
    """

    comparison = build_model_comparison(results)

    feature_importance = build_feature_importance_report(
        results
    )

    comparison_csv = write_comparison_csv(
        comparison
    )

    comparison_tex = write_comparison_latex(
        comparison
    )

    feature_importance_csv = write_feature_importance_csv(
        feature_importance
    )

    return (
        comparison_csv,
        comparison_tex,
        feature_importance_csv,
    )


def print_model_comparison(
    comparison: pd.DataFrame,
) -> None:
    """Print a compact model-comparison table."""

    display = comparison[
        [
            "model",
            "accuracy",
            "balanced_accuracy",
            "precision",
            "recall",
            "f1",
            "roc_auc",
        ]
    ].copy()

    display = display.rename(
        columns={
            "model": "Model",
            "accuracy": "Accuracy",
            "balanced_accuracy": "Bal. Acc.",
            "precision": "Precision",
            "recall": "Recall",
            "f1": "F1",
            "roc_auc": "ROC AUC",
        }
    )

    print()
    print("=" * 110)
    print("Baseline Tree Model Comparison")
    print("=" * 110)

    print(
        display.to_string(
            index=False,
            formatters={
                "Accuracy": lambda value: f"{value:.4f}",
                "Bal. Acc.": lambda value: f"{value:.4f}",
                "Precision": lambda value: f"{value:.4f}",
                "Recall": lambda value: f"{value:.4f}",
                "F1": lambda value: f"{value:.4f}",
                "ROC AUC": lambda value: f"{value:.4f}",
            },
        )
    )