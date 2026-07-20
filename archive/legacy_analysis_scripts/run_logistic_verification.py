"""
Canonical logistic-regression verification pipeline.

This script will eventually:

1. load the pseudonymised research dataset;
2. load the canonical train/test split;
3. rebuild the verified feature matrices;
4. fit logistic-regression models;
5. write comparison reports for independent R verification.
"""

from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

PROJECT_ROOT = Path(__file__).resolve().parent

RESEARCH_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "transition_research.csv"
)

SPLIT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "train_test_split.csv"
)


def main() -> None:
    """Load and verify the canonical input files."""

    print()
    print("Canonical Logistic Regression Verification")
    print("=" * 72)
    print()

    if not RESEARCH_FILE.exists():
        raise FileNotFoundError(
            f"Research dataset not found: {RESEARCH_FILE}"
        )

    if not SPLIT_FILE.exists():
        raise FileNotFoundError(
            f"Canonical split not found: {SPLIT_FILE}"
        )

    research = pd.read_csv(RESEARCH_FILE)
    split = pd.read_csv(SPLIT_FILE)

    print(f"Research rows:       {len(research)}")
    print(f"Research columns:    {len(research.columns)}")
    print(f"Split rows:          {len(split)}")
    print()

    required_research_columns = {
        "research_id",
        "current_subject_pass",
    }

    required_split_columns = {
        "research_id",
        "split",
    }

    missing_research_columns = (
        required_research_columns
        - set(research.columns)
    )

    missing_split_columns = (
        required_split_columns
        - set(split.columns)
    )

    if missing_research_columns:
        raise ValueError(
            "Research dataset is missing columns: "
            + ", ".join(sorted(missing_research_columns))
        )

    if missing_split_columns:
        raise ValueError(
            "Canonical split is missing columns: "
            + ", ".join(sorted(missing_split_columns))
        )

    print("Initial structural checks: PASS")
    print()

    if split["research_id"].duplicated().any():
        raise ValueError(
            "Canonical split contains duplicate research_id values."
        )

    unknown_split_ids = set(split["research_id"]) - set(
        research["research_id"]
    )

    if unknown_split_ids:
        raise ValueError(
            "Canonical split contains research_id values "
            "not found in the research dataset."
        )

    missing_split_ids = set(research["research_id"]) - set(
        split["research_id"]
    )

    if missing_split_ids:
        raise ValueError(
            "Some research observations are missing "
            "from the canonical split."
        )

    expected_split_values = {"train", "test"}
    actual_split_values = set(split["split"].dropna())

    if actual_split_values != expected_split_values:
        raise ValueError(
            "Unexpected split labels: "
            + ", ".join(sorted(actual_split_values))
        )

    analysis = research.merge(
        split,
        on="research_id",
        how="left",
        validate="one_to_one",
    )

    if analysis["split"].isna().any():
        raise ValueError(
            "Some rows have no split assignment after merging."
        )

    binary_columns = [
        "international_student",
        "has_previous_current_subject_attempt",
        "previous_current_subject_failure",
        "has_preparatory_subject",
        "prior_preparatory_subject_failure",
        "prior_preparatory_subject_pass",
    ]
    binary_mapping = {
        "yes": 1,
        "y": 1,
        "true": 1,
        "pass": 1,
        "passed": 1,
        "1": 1,
        "no": 0,
        "n": 0,
        "false": 0,
        "fail": 0,
        "failed": 0,
        "0": 0,
    }

    for column in binary_columns:
        cleaned = (
            analysis[column]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        converted = cleaned.map(binary_mapping)

        if converted.isna().any():
            invalid_values = sorted(
                cleaned.loc[converted.isna()].unique()
            )

            raise ValueError(
                f"Column {column!r} contains unrecognised "
                f"binary values: {invalid_values}"
            )

        analysis[column] = converted.astype(int)

    

    train = analysis.loc[
        analysis["split"] == "train"
    ].copy()

    test = analysis.loc[
        analysis["split"] == "test"
    ].copy()

    print("Canonical split verification")
    print("-" * 72)
    print(f"Training rows:       {len(train)}")
    print(f"Test rows:           {len(test)}")
    print()

    print("Training outcome counts")
    print(
        train["current_subject_pass"]
        .value_counts()
        .sort_index()
    )
    print()

    print("Test outcome counts")
    print(
        test["current_subject_pass"]
        .value_counts()
        .sort_index()
    )
    print()

    if len(train) != 1178:
        raise ValueError(
            f"Unexpected training row count: {len(train)}"
        )

    if len(test) != 295:
        raise ValueError(
            f"Unexpected test row count: {len(test)}"
        )

    print("Canonical split verification: PASS")
    print()
    
    
    categorical_columns = [
        "secondary_preparation_level",
        "secondary_school_mark_band",
    ]

    without_risk_columns = (
        binary_columns
        + categorical_columns
    )

    with_risk_columns = (
        without_risk_columns
        + ["risk_index"]
    )

    encoder_without_risk = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
                categorical_columns,
            ),
        ],
        remainder="passthrough",
        verbose_feature_names_out=False,
    )

    encoder_with_risk = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
                categorical_columns,
            ),
        ],
        remainder="passthrough",
        verbose_feature_names_out=False,
    )

    x_train_without_risk = encoder_without_risk.fit_transform(
        train[without_risk_columns]
    )

    x_test_without_risk = encoder_without_risk.transform(
        test[without_risk_columns]
    )

    x_train_with_risk = encoder_with_risk.fit_transform(
        train[with_risk_columns]
    )

    x_test_with_risk = encoder_with_risk.transform(
        test[with_risk_columns]
    )

    without_risk_feature_names = (
        encoder_without_risk
        .get_feature_names_out()
        .tolist()
    )

    with_risk_feature_names = (
        encoder_with_risk
        .get_feature_names_out()
        .tolist()
    )

    print("Logistic-regression feature matrices")
    print("-" * 72)
    print(
        "Without-risk training matrix: "
        f"{x_train_without_risk.shape[0]} x "
        f"{x_train_without_risk.shape[1]}"
    )
    print(
        "Without-risk test matrix:     "
        f"{x_test_without_risk.shape[0]} x "
        f"{x_test_without_risk.shape[1]}"
    )
    print(
        "With-risk training matrix:    "
        f"{x_train_with_risk.shape[0]} x "
        f"{x_train_with_risk.shape[1]}"
    )
    print(
        "With-risk test matrix:        "
        f"{x_test_with_risk.shape[0]} x "
        f"{x_test_with_risk.shape[1]}"
    )
    print()

    print("Without-risk feature names")
    for name in without_risk_feature_names:
        print(name)

    print()

    print("With-risk feature names")
    for name in with_risk_feature_names:
        print(name)

    print()

    if x_train_without_risk.shape != (1178, 15):
        raise ValueError(
            "Unexpected without-risk training matrix shape: "
            f"{x_train_without_risk.shape}"
        )

    if x_test_without_risk.shape != (295, 15):
        raise ValueError(
            "Unexpected without-risk test matrix shape: "
            f"{x_test_without_risk.shape}"
        )

    if x_train_with_risk.shape != (1178, 16):
        raise ValueError(
            "Unexpected with-risk training matrix shape: "
            f"{x_train_with_risk.shape}"
        )

    if x_test_with_risk.shape != (295, 16):
        raise ValueError(
            "Unexpected with-risk test matrix shape: "
            f"{x_test_with_risk.shape}"
        )

    print("Feature-matrix structure: PASS")
    print()
    # -----------------------------------------------------------------
    # Fit logistic regression without Risk Index
    # -----------------------------------------------------------------

    y_train = train["current_subject_pass"].astype(int)
    y_test = test["current_subject_pass"].astype(int)

    logistic_without_risk = LogisticRegression(
        C=float("inf"),
        solver="lbfgs",
        max_iter=10000,
    )

    logistic_without_risk.fit(
        x_train_without_risk,
        y_train,
    )

    probabilities = logistic_without_risk.predict_proba(
        x_test_without_risk
    )[:, 1]

    predictions = (
        probabilities >= 0.5
    ).astype(int)

    confusion = confusion_matrix(
        y_test,
        predictions,
        labels=[0, 1],
    )

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    balanced_accuracy = balanced_accuracy_score(
        y_test,
        predictions,
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0,
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0,
    )

    roc_auc = roc_auc_score(
        y_test,
        probabilities,
    )

    print("Canonical Logistic Regression — Without Risk")
    print("-" * 72)
    print("Confusion matrix")
    print(confusion)
    print()

    print(f"Accuracy          : {accuracy:.7f}")
    print(f"Balanced accuracy : {balanced_accuracy:.7f}")
    print(f"Precision         : {precision:.7f}")
    print(f"Recall            : {recall:.7f}")
    print(f"F1                : {f1:.7f}")
    print(f"ROC AUC           : {roc_auc:.7f}")

    # -----------------------------------------------------------------
    # Fit logistic regression with Risk Index
    # -----------------------------------------------------------------

    logistic_with_risk = LogisticRegression(
        C=float("inf"),
        solver="lbfgs",
        max_iter=10000,
    )

    logistic_with_risk.fit(
        x_train_with_risk,
        y_train,
    )

    probabilities_with_risk = (
        logistic_with_risk.predict_proba(
            x_test_with_risk
        )[:, 1]
    )

    predictions_with_risk = (
        probabilities_with_risk >= 0.5
    ).astype(int)

    confusion_with_risk = confusion_matrix(
        y_test,
        predictions_with_risk,
        labels=[0, 1],
    )

    accuracy_with_risk = accuracy_score(
        y_test,
        predictions_with_risk,
    )

    balanced_accuracy_with_risk = (
        balanced_accuracy_score(
            y_test,
            predictions_with_risk,
        )
    )

    precision_with_risk = precision_score(
        y_test,
        predictions_with_risk,
        zero_division=0,
    )

    recall_with_risk = recall_score(
        y_test,
        predictions_with_risk,
        zero_division=0,
    )

    f1_with_risk = f1_score(
        y_test,
        predictions_with_risk,
        zero_division=0,
    )

    roc_auc_with_risk = roc_auc_score(
        y_test,
        probabilities_with_risk,
    )

    print()
    print("Canonical Logistic Regression — With Risk")
    print("-" * 72)
    print("Confusion matrix")
    print(confusion_with_risk)
    print()

    print(
        f"Accuracy          : "
        f"{accuracy_with_risk:.7f}"
    )
    print(
        f"Balanced accuracy : "
        f"{balanced_accuracy_with_risk:.7f}"
    )
    print(
        f"Precision         : "
        f"{precision_with_risk:.7f}"
    )
    print(
        f"Recall            : "
        f"{recall_with_risk:.7f}"
    )
    print(
        f"F1                : "
        f"{f1_with_risk:.7f}"
    )
    print(
        f"ROC AUC           : "
        f"{roc_auc_with_risk:.7f}"
    )
    
    probability_difference = abs(
        probabilities_with_risk - probabilities
    )

    risk_feature_position = (
        with_risk_feature_names.index("risk_index")
    )

    risk_coefficient = (
        logistic_with_risk.coef_[0][risk_feature_position]
    )

    print()
    print("Risk Index diagnostic")
    print("-" * 72)
    print(
        "Maximum probability difference: "
        f"{probability_difference.max():.12f}"
    )
    print(
        "Mean probability difference:    "
        f"{probability_difference.mean():.12f}"
    )
    print(
        "Risk Index coefficient:         "
        f"{risk_coefficient:.12f}"
    )
    print(
    "Intercept (without risk):       "
    f"{logistic_without_risk.intercept_[0]:.12f}"
)

    print(
        "Intercept (with risk):          "
        f"{logistic_with_risk.intercept_[0]:.12f}"
    )

    print()

    print("Coefficient comparison")
    print("-" * 72)

    for name, coef in zip(
        without_risk_feature_names,
        logistic_without_risk.coef_[0],
    ):
    
        print(f"{name:<45}{coef: .8f}")

    print()

    for name, coef in zip(
        with_risk_feature_names,
        logistic_with_risk.coef_[0],
    ):
        print(f"{name:<45}{coef: .8f}")
    
if __name__ == "__main__":
    main()