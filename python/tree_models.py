"""Decision Tree and Random Forest modelling utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.tree import DecisionTreeClassifier

# from python.ml import DataSplit, apply_split
from python.ml_split import DataSplit, apply_split
from python.tree_data import TreeDataset


DEFAULT_RANDOM_SEED = 33130


@dataclass(frozen=True)
class TreeModelResult:
    """Results from a fitted tree-based classifier."""

    dataset_name: str
    model_name: str
    model: Any
    metrics: dict[str, float | int]
    confusion_matrix: pd.DataFrame
    feature_importance: pd.DataFrame


def calculate_metrics(
    y_true: pd.Series,
    predictions: pd.Series,
    probabilities: pd.Series,
) -> dict[str, float | int]:
    """Calculate classification metrics for held-out test data."""

    return {
        "test_rows": int(len(y_true)),
        "passes": int((y_true == 1).sum()),
        "non_passes": int((y_true == 0).sum()),
        "accuracy": float(
            accuracy_score(y_true, predictions)
        ),
        "balanced_accuracy": float(
            balanced_accuracy_score(y_true, predictions)
        ),
        "precision": float(
            precision_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),
        "f1": float(
            f1_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),
        "roc_auc": float(
            roc_auc_score(y_true, probabilities)
        ),
    }


def build_confusion_matrix(
    y_true: pd.Series,
    predictions: pd.Series,
) -> pd.DataFrame:
    """Return a labelled confusion matrix."""

    matrix = confusion_matrix(
        y_true,
        predictions,
        labels=[0, 1],
    )

    return pd.DataFrame(
        matrix,
        index=[
            "Actual Non-pass",
            "Actual Pass",
        ],
        columns=[
            "Predicted Non-pass",
            "Predicted Pass",
        ],
    )


def build_feature_importance(
    model: Any,
    feature_names: list[str],
) -> pd.DataFrame:
    """Return feature importances in descending order."""

    importance = pd.DataFrame(
        {
            "feature": feature_names,
            "importance": model.feature_importances_,
        }
    )

    return importance.sort_values(
        "importance",
        ascending=False,
    ).reset_index(drop=True)


def fit_and_evaluate(
    *,
    dataset: TreeDataset,
    split: DataSplit,
    model: Any,
    model_name: str,
) -> TreeModelResult:
    """Fit one model and evaluate it only on held-out test data."""

    X_train, X_test, y_train, y_test = apply_split(
        X=dataset.X,
        y=dataset.y,
        split=split,
    )

    model.fit(X_train, y_train)

    predictions = pd.Series(
        model.predict(X_test),
        index=y_test.index,
        name="prediction",
    )

    probabilities = pd.Series(
        model.predict_proba(X_test)[:, 1],
        index=y_test.index,
        name="pass_probability",
    )

    metrics = calculate_metrics(
        y_true=y_test,
        predictions=predictions,
        probabilities=probabilities,
    )

    labelled_confusion_matrix = build_confusion_matrix(
        y_true=y_test,
        predictions=predictions,
    )

    feature_importance = build_feature_importance(
        model=model,
        feature_names=list(X_train.columns),
    )

    return TreeModelResult(
        dataset_name=dataset.name,
        model_name=model_name,
        model=model,
        metrics=metrics,
        confusion_matrix=labelled_confusion_matrix,
        feature_importance=feature_importance,
    )


def run_decision_tree(
    dataset: TreeDataset,
    split: DataSplit,
    random_seed: int = DEFAULT_RANDOM_SEED,
) -> TreeModelResult:
    """Fit and evaluate a controlled Decision Tree."""

    model = DecisionTreeClassifier(
        max_depth=4,
        min_samples_leaf=20,
        class_weight="balanced",
        random_state=random_seed,
    )

    return fit_and_evaluate(
        dataset=dataset,
        split=split,
        model=model,
        model_name="Decision Tree",
    )


def run_random_forest(
    dataset: TreeDataset,
    split: DataSplit,
    random_seed: int = DEFAULT_RANDOM_SEED,
) -> TreeModelResult:
    """Fit and evaluate a Random Forest."""

    model = RandomForestClassifier(
        n_estimators=500,
        max_depth=None,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=random_seed,
        n_jobs=-1,
    )

    return fit_and_evaluate(
        dataset=dataset,
        split=split,
        model=model,
        model_name="Random Forest",
    )