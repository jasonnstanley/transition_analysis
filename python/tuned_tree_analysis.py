"""Tune tree models using cross-validation on training data only."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from python.ml_split import (
    create_stratified_split,
    write_split,
)
from python.research_io import load_research_data
from python.schema import (
    load_research_schema,
    release_output_file,
)
from python.splash import splash
from python.tree_data import build_tree_datasets
from python.tree_tuning import (
    TunedTreeResult,
    tune_decision_tree,
    tune_random_forest,
)
from python.feature_reporting import (
    print_tuned_importance_summary,
    write_tuned_feature_reports,
)
from python.analysis_audit import (
    AnalysisTimer,
    build_analysis_audit,
    write_analysis_audit,
)
from python.roc_reporting import write_tuned_roc_reports

REPORT_DATA_DIRECTORY = Path("reports/data")

TUNING_CSV = (
    REPORT_DATA_DIRECTORY
    / "tuned_tree_models.csv"
)

PARAMETERS_JSON = (
    REPORT_DATA_DIRECTORY
    / "tuned_tree_parameters.json"
)

TUNING_AUDIT = Path("logs/tree_tuning_audit.json")
SPLIT_CSV = Path("data/processed/train_test_split.csv")



def print_tuned_result(tuned: TunedTreeResult) -> None:
    """Print one tuned model result."""

    result = tuned.result
    metrics = result.metrics

    print()
    print("=" * 72)
    print(f"{result.model_name} — {result.dataset_name}")
    print("=" * 72)

    print(
        f"Best cross-validated ROC AUC : "
        f"{tuned.best_cv_score:.4f}"
    )
    print(f"Cross-validation folds       : {tuned.cv_folds}")
    print(f"Selection metric             : {tuned.scoring}")

    print()
    print("Best parameters")
    print("-" * 72)

    for parameter, value in tuned.best_parameters.items():
        print(f"{parameter:<24}: {value}")

    print()
    print("Untouched test-set performance")
    print("-" * 72)
    print(f"Accuracy           : {metrics['accuracy']:.4f}")
    print(
        f"Balanced Accuracy  : "
        f"{metrics['balanced_accuracy']:.4f}"
    )
    print(f"Precision          : {metrics['precision']:.4f}")
    print(f"Recall             : {metrics['recall']:.4f}")
    print(f"F1                 : {metrics['f1']:.4f}")
    print(f"ROC AUC            : {metrics['roc_auc']:.4f}")

    print()
    print("Confusion Matrix")
    print("-" * 72)
    print(result.confusion_matrix.to_string())


def build_tuning_summary(
    tuned_results: list[TunedTreeResult],
) -> pd.DataFrame:
    """Build a comparison table for the four tuned models."""

    rows: list[dict[str, object]] = []

    for tuned in tuned_results:
        result = tuned.result
        metrics = result.metrics

        rows.append(
            {
                "model": result.model_name,
                "dataset": result.dataset_name,
                "cv_folds": tuned.cv_folds,
                "selection_metric": tuned.scoring,
                "best_cv_roc_auc": tuned.best_cv_score,
                "test_accuracy": metrics["accuracy"],
                "test_balanced_accuracy": metrics[
                    "balanced_accuracy"
                ],
                "test_precision": metrics["precision"],
                "test_recall": metrics["recall"],
                "test_f1": metrics["f1"],
                "test_roc_auc": metrics["roc_auc"],
            }
        )

    return pd.DataFrame(rows)


def write_tuning_reports(
    tuned_results: list[TunedTreeResult],
) -> tuple[Path, Path]:
    """Write tuning summary and selected parameters."""

    REPORT_DATA_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary = build_tuning_summary(tuned_results)

    summary.to_csv(
        TUNING_CSV,
        index=False,
    )

    parameters = [
        {
            "model": tuned.result.model_name,
            "dataset": tuned.result.dataset_name,
            "best_cv_score": tuned.best_cv_score,
            "scoring": tuned.scoring,
            "cv_folds": tuned.cv_folds,
            "best_parameters": tuned.best_parameters,
        }
        for tuned in tuned_results
    ]

    PARAMETERS_JSON.write_text(
        json.dumps(
            parameters,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    return TUNING_CSV, PARAMETERS_JSON


def main() -> None:
    timer = AnalysisTimer()
    timer.start()

    schema = load_research_schema()
    dataframe = load_research_data()

    research_id_column = schema[
        "identifiers"
    ][
        "research_identifier"
    ][
        "column"
    ]

    splash(
        schema=schema,
        dataframe=dataframe,
        identifier_column=research_id_column,
    )

    without_risk, with_risk = build_tree_datasets()

    split = create_stratified_split(
        target=without_risk.y,
    )
    split_path = write_split(
        split=split,
        research_ids=dataframe[research_id_column],
        output_file=SPLIT_CSV,
    )
    print()
    print("Cross-validated tree tuning")
    print("-" * 72)
    print(f"Training rows : {len(split.train_indices):,}")
    print(f"Test rows     : {len(split.test_indices):,}")
    print("CV folds      : 5")
    print("Selection     : ROC AUC")
    print()
    print(
        "The test rows are excluded from hyperparameter selection."
    )

    tuned_results = [
        tune_decision_tree(
            dataset=without_risk,
            split=split,
        ),
        tune_decision_tree(
            dataset=with_risk,
            split=split,
        ),
        tune_random_forest(
            dataset=without_risk,
            split=split,
        ),
        tune_random_forest(
            dataset=with_risk,
            split=split,
        ),
    ]

    for tuned in tuned_results:
        print_tuned_result(tuned)

    csv_path, parameters_path = write_tuning_reports(
        tuned_results
    )
    print_tuned_importance_summary(
        tuned_results
    )

    (
        importance_long_path,
        importance_wide_path,
        importance_tex_path,
    ) = write_tuned_feature_reports(
        tuned_results
    )
    (
        roc_points_path,
        roc_summary_path,
        roc_tex_path,
        roc_figure_path,
    ) = write_tuned_roc_reports(
        tuned_results=tuned_results,
        without_risk=without_risk,
        with_risk=with_risk,
        split=split,
    )
    execution_seconds = timer.stop()

    model_audit_rows = [
        {
            "model": tuned.result.model_name,
            "dataset": tuned.result.dataset_name,
            "best_cv_score": tuned.best_cv_score,
            "best_parameters": tuned.best_parameters,
            "test_metrics": tuned.result.metrics,
        }
        for tuned in tuned_results
    ]

    research_dataset_path = release_output_file(
        schema,
        "research",
    )

    audit_record = build_analysis_audit(
        schema=schema,
        analysis_name="Cross-validated tree-model tuning",
        dataset_path=research_dataset_path,
        dataset_rows=len(dataframe),
        dataset_columns=len(dataframe.columns),
        random_seed=split.random_seed,
        test_size=split.test_size,
        training_rows=len(split.train_indices),
        test_rows=len(split.test_indices),
        cv_folds=5,
        selection_metric="roc_auc",
        models=model_audit_rows,
        output_files=[
            csv_path,
            parameters_path,
            importance_long_path,
            importance_wide_path,
            importance_tex_path,
            roc_points_path,
            roc_summary_path,
            roc_tex_path,
            roc_figure_path,
            split_path,
        ],
        execution_seconds=execution_seconds,
    )

    audit_path = write_analysis_audit(
        audit=audit_record,
        output_path=TUNING_AUDIT,
    )
    print()
    print("Tuning reports written")
    print("-" * 72)
    print(f"Summary CSV:     {csv_path}")
    print(f"Parameters JSON: {parameters_path}")
    print(
        f"Feature importance long:  "
        f"{importance_long_path}"
    )
    print(
        f"Feature importance wide:  "
        f"{importance_wide_path}"
    )
    print(
        f"Feature importance TeX:   "
        f"{importance_tex_path}"
    )
    print(f"ROC curve points:          {roc_points_path}")
    print(f"ROC summary CSV:           {roc_summary_path}")
    print(f"ROC summary TeX:           {roc_tex_path}")
    print(f"ROC comparison figure:     {roc_figure_path}")
    print(f"Analysis audit:            {audit_path}")
    print(f"Canonical split:            {split_path}")
    
if __name__ == "__main__":
    main()