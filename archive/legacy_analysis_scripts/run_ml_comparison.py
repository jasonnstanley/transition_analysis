"""
Compare Decision Tree and Random Forest models
using identical train/test splits.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

from python.forests import fit_random_forest
from python.io import load_data
from python.ml import split_data
from python.trees import fit_decision_tree


OUTPUTS = Path("outputs")
FIGURES = Path("figures")

OUTPUTS.mkdir(exist_ok=True)
FIGURES.mkdir(exist_ok=True)


def yn_to_number(series):
    """
    Convert common Yes/No values to 1/0.
    """

    return series.map(
        {
            "Y": 1,
            "N": 0,
            "Yes": 1,
            "No": 0,
        }
    )


def prepare_X(df, features):
    """
    Select and prepare predictor columns.
    """

    X = df[features].copy()

    binary_columns = [
        "Has 35010",
        "Previous 33130 Fail",
        "International Student",
    ]

    for column in binary_columns:
        if column in X.columns:
            X[column] = yn_to_number(X[column])

    return X


def calculate_metrics(model, X_test, y_test):
    """
    Calculate classification metrics for one model.
    """

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    return {
        "Accuracy": accuracy_score(y_test, predictions),
        "Balanced Accuracy": balanced_accuracy_score(
            y_test,
            predictions,
        ),
        "Precision": precision_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "Recall": recall_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "F1": f1_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "ROC AUC": roc_auc_score(
            y_test,
            probabilities,
        ),
    }


def main():
    df = load_data()
    y = df["Pass 33130"]

    feature_sets = {
        "With Risk Index": [
            "Risk Index",
            "Has 35010",
            "Previous 33130 Fail",
            "International Student",
        ],
        "Without Risk Index": [
            "Has 35010",
            "Previous 33130 Fail",
            "International Student",
        ],
    }

    comparison_rows = []

    figure, axis = plt.subplots(figsize=(9, 7))

    for feature_set_name, features in feature_sets.items():
        X = prepare_X(df, features)

        X_train, X_test, y_train, y_test = split_data(
            X,
            y,
        )

        models = {
            "Decision Tree": fit_decision_tree(
                X_train,
                y_train,
                max_depth=3,
                random_state=42,
            ),
            "Random Forest": fit_random_forest(
                X_train,
                y_train,
                n_estimators=500,
                random_state=42,
            ),
        }

        for model_name, model in models.items():
            full_name = f"{model_name} — {feature_set_name}"

            metrics = calculate_metrics(
                model,
                X_test,
                y_test,
            )

            comparison_rows.append(
                {
                    "Model": model_name,
                    "Feature Set": feature_set_name,
                    **metrics,
                }
            )

            probabilities = model.predict_proba(X_test)[:, 1]

            false_positive_rate, true_positive_rate, _ = roc_curve(
                y_test,
                probabilities,
            )

            axis.plot(
                false_positive_rate,
                true_positive_rate,
                label=(
                    f"{full_name} "
                    f"(AUC = {metrics['ROC AUC']:.3f})"
                ),
            )

    axis.plot(
        [0, 1],
        [0, 1],
        linestyle="--",
        label="Chance",
    )

    axis.set_xlabel("False Positive Rate")
    axis.set_ylabel("True Positive Rate")
    axis.set_title("Decision Tree and Random Forest ROC Comparison")
    axis.legend()
    axis.grid(alpha=0.3)

    figure.tight_layout()

    figure_file = FIGURES / "fig09_ml_roc_comparison.png"

    figure.savefig(
        figure_file,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)

    comparison = pd.DataFrame(comparison_rows)

    comparison = comparison.sort_values(
        by="ROC AUC",
        ascending=False,
    ).reset_index(drop=True)

    csv_file = OUTPUTS / "ml_model_comparison.csv"
    latex_file = OUTPUTS / "ml_model_comparison.tex"

    comparison.to_csv(
        csv_file,
        index=False,
    )

    comparison.to_latex(
        latex_file,
        index=False,
        float_format="%.3f",
    )

    print()
    print("Machine Learning Model Comparison")
    print("=================================")
    print(comparison.round(3))

    print()
    print(f"Saved {csv_file}")
    print(f"Saved {latex_file}")
    print(f"Saved {figure_file}")


if __name__ == "__main__":
    main()