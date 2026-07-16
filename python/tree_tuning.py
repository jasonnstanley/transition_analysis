"""Cross-validated tuning for Decision Tree and Random Forest models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import (
    GridSearchCV,
    RandomizedSearchCV,
    StratifiedKFold,
)
from sklearn.tree import DecisionTreeClassifier

from python.ml_split import DataSplit, apply_split
from python.tree_data import TreeDataset
from python.tree_models import (
    TreeModelResult,
    build_confusion_matrix,
    build_feature_importance,
    calculate_metrics,
)


DEFAULT_RANDOM_SEED = 33130
DEFAULT_CV_FOLDS = 5


@dataclass(frozen=True)
class TunedTreeResult:
    """A tuned model plus its cross-validation information."""

    result: TreeModelResult
    best_parameters: dict[str, Any]
    best_cv_score: float
    scoring: str
    cv_folds: int


def build_cross_validation(
    random_seed: int = DEFAULT_RANDOM_SEED,
    cv_folds: int = DEFAULT_CV_FOLDS,
) -> StratifiedKFold:
    """Create reproducible stratified cross-validation folds."""

    return StratifiedKFold(
        n_splits=cv_folds,
        shuffle=True,
        random_state=random_seed,
    )


def evaluate_tuned_model(
    *,
    dataset: TreeDataset,
    split: DataSplit,
    model: Any,
    model_name: str,
) -> TreeModelResult:
    """
    Evaluate an already-fitted tuned model on untouched test data.
    """

    _, X_test, _, y_test = apply_split(
        X=dataset.X,
        y=dataset.y,
        split=split,
    )

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
        feature_names=list(X_test.columns),
    )

    return TreeModelResult(
        dataset_name=dataset.name,
        model_name=model_name,
        model=model,
        metrics=metrics,
        confusion_matrix=labelled_confusion_matrix,
        feature_importance=feature_importance,
    )


def tune_decision_tree(
    *,
    dataset: TreeDataset,
    split: DataSplit,
    random_seed: int = DEFAULT_RANDOM_SEED,
    cv_folds: int = DEFAULT_CV_FOLDS,
) -> TunedTreeResult:
    """Tune a Decision Tree using grid search on training data only."""

    X_train, _, y_train, _ = apply_split(
        X=dataset.X,
        y=dataset.y,
        split=split,
    )

    estimator = DecisionTreeClassifier(
        class_weight="balanced",
        random_state=random_seed,
    )

    parameter_grid = {
        "criterion": [
            "gini",
            "entropy",
        ],
        "max_depth": [
            2,
            3,
            4,
            5,
            6,
            None,
        ],
        "min_samples_split": [
            2,
            10,
            20,
            40,
        ],
        "min_samples_leaf": [
            5,
            10,
            20,
            30,
            40,
        ],
    }

    search = GridSearchCV(
        estimator=estimator,
        param_grid=parameter_grid,
        scoring="roc_auc",
        cv=build_cross_validation(
            random_seed=random_seed,
            cv_folds=cv_folds,
        ),
        refit=True,
        n_jobs=-1,
        return_train_score=True,
    )

    search.fit(X_train, y_train)

    result = evaluate_tuned_model(
        dataset=dataset,
        split=split,
        model=search.best_estimator_,
        model_name="Tuned Decision Tree",
    )

    return TunedTreeResult(
        result=result,
        best_parameters=dict(search.best_params_),
        best_cv_score=float(search.best_score_),
        scoring="roc_auc",
        cv_folds=cv_folds,
    )


def tune_random_forest(
    *,
    dataset: TreeDataset,
    split: DataSplit,
    random_seed: int = DEFAULT_RANDOM_SEED,
    cv_folds: int = DEFAULT_CV_FOLDS,
) -> TunedTreeResult:
    """
    Tune a Random Forest using reproducible randomised search.

    Randomised search avoids testing every possible combination while
    still using cross-validation rather than hand-selecting settings.
    """

    X_train, _, y_train, _ = apply_split(
        X=dataset.X,
        y=dataset.y,
        split=split,
    )

    estimator = RandomForestClassifier(
        class_weight="balanced",
        random_state=random_seed,
        n_jobs=-1,
    )

    parameter_distributions = {
        "n_estimators": [
            200,
            400,
            600,
            800,
            1000,
        ],
        "max_depth": [
            3,
            5,
            8,
            12,
            None,
        ],
        "min_samples_split": [
            2,
            5,
            10,
            20,
        ],
        "min_samples_leaf": [
            2,
            5,
            10,
            20,
        ],
        "max_features": [
            "sqrt",
            "log2",
            None,
        ],
    }

    search = RandomizedSearchCV(
        estimator=estimator,
        param_distributions=parameter_distributions,
        n_iter=40,
        scoring="roc_auc",
        cv=build_cross_validation(
            random_seed=random_seed,
            cv_folds=cv_folds,
        ),
        refit=True,
        random_state=random_seed,
        n_jobs=-1,
        return_train_score=True,
    )

    search.fit(X_train, y_train)

    result = evaluate_tuned_model(
        dataset=dataset,
        split=split,
        model=search.best_estimator_,
        model_name="Tuned Random Forest",
    )

    return TunedTreeResult(
        result=result,
        best_parameters=dict(search.best_params_),
        best_cv_score=float(search.best_score_),
        scoring="roc_auc",
        cv_folds=cv_folds,
    )