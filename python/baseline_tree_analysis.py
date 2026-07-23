"""Run Decision Tree and Random Forest comparisons."""

from __future__ import annotations

# from python.ml import create_stratified_split
from python.ml_split import create_stratified_split
from python.schema import load_research_schema
from python.splash import splash
from python.tree_data import build_tree_datasets
# from python.trees import (
#    TreeModelResult,
#    run_decision_tree,
#    run_random_forest,
# )
from python.tree_models import (
    TreeModelResult,
    run_decision_tree,
    run_random_forest,
)
from python.tree_reporting import (
    build_model_comparison,
    print_model_comparison,
    write_baseline_reports,
)

def print_result(result: TreeModelResult) -> None:
    """Print one held-out model result."""

    print()
    print("=" * 72)
    print(f"{result.model_name} — {result.dataset_name}")
    print("=" * 72)

    metrics = result.metrics

    print(f"Test rows          : {metrics['test_rows']:,}")
    print(f"Passes             : {metrics['passes']:,}")
    print(f"Non-passes         : {metrics['non_passes']:,}")
    print(f"Accuracy           : {metrics['accuracy']:.4f}")
    print(
        "Balanced Accuracy  : "
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

    print()
    print("Top Feature Importances")
    print("-" * 72)
    print(
        result.feature_importance.head(10).to_string(
            index=False,
            formatters={
                "importance": lambda value: f"{value:.4f}",
            },
        )
    )


def main() -> None:
    schema = load_research_schema()

    without_risk, with_risk = build_tree_datasets()

    identifier_column = schema[
        "identifiers"
    ][
        "research_identifier"
    ][
        "column"
    ]

    # The splash loads the full research dataset only for its summary.
    from python.research_io import load_research_data

    research_dataframe = load_research_data()

    splash(
        schema=schema,
        dataframe=research_dataframe,
        identifier_column=identifier_column,
    )

    # Create one split from the shared target vector.
    split = create_stratified_split(
        target=without_risk.y,
    )

    print()
    print("Machine-learning split")
    print("-" * 72)
    print(f"Random seed : {split.random_seed}")
    print(f"Test size   : {split.test_size:.0%}")
    print(f"Training    : {len(split.train_indices):,}")
    print(f"Testing     : {len(split.test_indices):,}")

    results = [
        run_decision_tree(
            dataset=without_risk,
            split=split,
        ),
        run_decision_tree(
            dataset=with_risk,
            split=split,
        ),
        run_random_forest(
            dataset=without_risk,
            split=split,
        ),
        run_random_forest(
            dataset=with_risk,
            split=split,
        ),
    ]

    for result in results:
        print_result(result)

    comparison = build_model_comparison(results)

    print_model_comparison(comparison)

    (
        comparison_csv,
        comparison_tex,
        feature_importance_csv,
    ) = write_baseline_reports(results)

    print()
    print("Baseline reports written")
    print("-" * 72)
    print(f"Model comparison CSV: {comparison_csv}")
    print(f"Model comparison TeX: {comparison_tex}")
    print(
        "Feature importance CSV: "
        f"{feature_importance_csv}"
    )
    
    
if __name__ == "__main__":
    main()