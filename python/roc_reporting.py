"""ROC comparison reporting for tuned tree-based models."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import auc, roc_curve

from python.feature_reporting import tuned_model_label
from python.ml_split import DataSplit, apply_split
from python.tree_data import TreeDataset
from python.tree_tuning import TunedTreeResult


DEFAULT_REPORT_DIRECTORY = Path("reports")
DEFAULT_FIGURE_DIRECTORY = Path("figures")

DEFAULT_ROC_POINTS_CSV = (
    DEFAULT_REPORT_DIRECTORY
    / "tuned_roc_curve_points.csv"
)

DEFAULT_ROC_SUMMARY_CSV = (
    DEFAULT_REPORT_DIRECTORY
    / "tuned_roc_summary.csv"
)

DEFAULT_ROC_SUMMARY_TEX = (
    DEFAULT_REPORT_DIRECTORY
    / "tuned_roc_summary.tex"
)

DEFAULT_ROC_FIGURE = (
    DEFAULT_FIGURE_DIRECTORY
    / "fig_tuned_tree_roc_comparison.png"
)


class RocReportingError(ValueError):
    """Raised when ROC reporting cannot be completed safely."""


def build_dataset_lookup(
    without_risk: TreeDataset,
    with_risk: TreeDataset,
) -> dict[str, TreeDataset]:
    """Create a lookup using the dataset names stored in model results."""

    return {
        without_risk.name: without_risk,
        with_risk.name: with_risk,
    }


def build_roc_reports(
    *,
    tuned_results: list[TunedTreeResult],
    dataset_lookup: dict[str, TreeDataset],
    split: DataSplit,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Calculate ROC curve points and summary values.

    The tuned estimators are already fitted. Probabilities are calculated
    only for the untouched test rows.
    """

    point_frames: list[pd.DataFrame] = []
    summary_rows: list[dict[str, object]] = []

    for tuned in tuned_results:
        result = tuned.result
        dataset_name = result.dataset_name

        if dataset_name not in dataset_lookup:
            raise RocReportingError(
                f"No modelling dataset found for '{dataset_name}'."
            )

        dataset = dataset_lookup[dataset_name]

        _, X_test, _, y_test = apply_split(
            X=dataset.X,
            y=dataset.y,
            split=split,
        )

        probabilities = result.model.predict_proba(
            X_test
        )[:, 1]

        false_positive_rate, true_positive_rate, thresholds = (
            roc_curve(
                y_test,
                probabilities,
                pos_label=1,
            )
        )

        roc_auc = auc(
            false_positive_rate,
            true_positive_rate,
        )

        label = tuned_model_label(tuned)

        points = pd.DataFrame(
            {
                "model": label,
                "dataset": dataset_name,
                "false_positive_rate": false_positive_rate,
                "true_positive_rate": true_positive_rate,
                "threshold": thresholds,
            }
        )

        point_frames.append(points)

        summary_rows.append(
            {
                "model": label,
                "dataset": dataset_name,
                "roc_auc": float(roc_auc),
                "test_rows": int(len(y_test)),
                "test_passes": int((y_test == 1).sum()),
                "test_non_passes": int((y_test == 0).sum()),
                "cv_roc_auc": float(tuned.best_cv_score),
            }
        )

    curve_points = pd.concat(
        point_frames,
        ignore_index=True,
    )

    summary = pd.DataFrame(
        summary_rows
    ).sort_values(
        "roc_auc",
        ascending=False,
    ).reset_index(drop=True)

    return curve_points, summary


def write_roc_points_csv(
    dataframe: pd.DataFrame,
    output_path: str | Path = DEFAULT_ROC_POINTS_CSV,
) -> Path:
    """Write all ROC coordinates and thresholds to CSV."""

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


def write_roc_summary_csv(
    dataframe: pd.DataFrame,
    output_path: str | Path = DEFAULT_ROC_SUMMARY_CSV,
) -> Path:
    """Write the model-level ROC summary to CSV."""

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


def write_roc_summary_latex(
    dataframe: pd.DataFrame,
    output_path: str | Path = DEFAULT_ROC_SUMMARY_TEX,
) -> Path:
    """Write the ROC summary as a LaTeX table."""

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    latex_table = dataframe[
        [
            "model",
            "cv_roc_auc",
            "roc_auc",
            "test_rows",
        ]
    ].rename(
        columns={
            "model": "Model",
            "cv_roc_auc": "CV ROC AUC",
            "roc_auc": "Test ROC AUC",
            "test_rows": "Test Rows",
        }
    )

    latex = latex_table.to_latex(
        index=False,
        float_format="%.4f",
        caption=(
            "ROC AUC comparison for cross-validated "
            "Decision Tree and Random Forest models."
        ),
        label="tab:tuned_tree_roc_summary",
        position="htbp",
        escape=True,
    )

    path.write_text(
        latex,
        encoding="utf-8",
    )

    return path


def plot_roc_comparison(
    *,
    curve_points: pd.DataFrame,
    summary: pd.DataFrame,
    output_path: str | Path = DEFAULT_ROC_FIGURE,
) -> Path:
    """Create one publication-ready ROC comparison figure."""

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    figure, axis = plt.subplots(
        figsize=(8.5, 7.0),
    )

    auc_lookup = dict(
        zip(
            summary["model"],
            summary["roc_auc"],
        )
    )

    for model_name in curve_points["model"].unique():
        model_points = curve_points[
            curve_points["model"] == model_name
        ]

        model_auc = auc_lookup[model_name]

        axis.plot(
            model_points["false_positive_rate"],
            model_points["true_positive_rate"],
            linewidth=2,
            label=f"{model_name} (AUC = {model_auc:.3f})",
        )

    axis.plot(
        [0, 1],
        [0, 1],
        linestyle="--",
        linewidth=1.2,
        label="Chance",
    )

    axis.set_title(
        "ROC Comparison of Tuned Tree-Based Models"
    )
    axis.set_xlabel(
        "False Positive Rate"
    )
    axis.set_ylabel(
        "True Positive Rate"
    )

    axis.set_xlim(0.0, 1.0)
    axis.set_ylim(0.0, 1.02)
    axis.grid(
        visible=True,
        alpha=0.25,
    )
    axis.legend(
        loc="lower right",
        frameon=True,
    )

    figure.tight_layout()

    figure.savefig(
        path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)

    return path


def print_roc_summary(
    summary: pd.DataFrame,
) -> None:
    """Print a compact ROC comparison table."""

    display = summary[
        [
            "model",
            "cv_roc_auc",
            "roc_auc",
        ]
    ].rename(
        columns={
            "model": "Model",
            "cv_roc_auc": "CV ROC AUC",
            "roc_auc": "Test ROC AUC",
        }
    )

    print()
    print("=" * 88)
    print("Tuned ROC Comparison")
    print("=" * 88)

    print(
        display.to_string(
            index=False,
            formatters={
                "CV ROC AUC": lambda value: f"{value:.4f}",
                "Test ROC AUC": lambda value: f"{value:.4f}",
            },
        )
    )


def write_tuned_roc_reports(
    *,
    tuned_results: list[TunedTreeResult],
    without_risk: TreeDataset,
    with_risk: TreeDataset,
    split: DataSplit,
) -> tuple[Path, Path, Path, Path]:
    """Generate all tuned ROC reports and the comparison figure."""

    dataset_lookup = build_dataset_lookup(
        without_risk=without_risk,
        with_risk=with_risk,
    )

    curve_points, summary = build_roc_reports(
        tuned_results=tuned_results,
        dataset_lookup=dataset_lookup,
        split=split,
    )

    print_roc_summary(summary)

    points_path = write_roc_points_csv(
        curve_points
    )

    summary_path = write_roc_summary_csv(
        summary
    )

    latex_path = write_roc_summary_latex(
        summary
    )

    figure_path = plot_roc_comparison(
        curve_points=curve_points,
        summary=summary,
    )

    return (
        points_path,
        summary_path,
        latex_path,
        figure_path,
    )