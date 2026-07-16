"""Shared train/test splitting utilities for machine-learning models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


DEFAULT_TEST_SIZE = 0.20
DEFAULT_RANDOM_SEED = 33130


class MachineLearningError(ValueError):
    """Raised when machine-learning data cannot be split safely."""


@dataclass(frozen=True)
class DataSplit:
    """Row indices defining a reproducible train/test split."""

    train_indices: pd.Index
    test_indices: pd.Index
    random_seed: int
    test_size: float


def create_stratified_split(
    target: pd.Series,
    test_size: float = DEFAULT_TEST_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
) -> DataSplit:
    """
    Create a stratified train/test split using row indices.

    Storing indices rather than separate feature matrices allows all
    models to use exactly the same training and testing students.
    """

    if target.empty:
        raise MachineLearningError(
            "Cannot split an empty target vector."
        )

    if target.isna().any():
        raise MachineLearningError(
            "The target vector contains missing values."
        )

    class_counts = target.value_counts()

    if len(class_counts) != 2:
        raise MachineLearningError(
            "The target must contain exactly two outcome classes."
        )

    if (class_counts < 2).any():
        raise MachineLearningError(
            "Each target class must contain at least two observations."
        )

    indices = target.index

    train_indices, test_indices = train_test_split(
        indices,
        test_size=test_size,
        random_state=random_seed,
        stratify=target,
    )

    return DataSplit(
        train_indices=pd.Index(train_indices),
        test_indices=pd.Index(test_indices),
        random_seed=random_seed,
        test_size=test_size,
    )


def apply_split(
    X: pd.DataFrame,
    y: pd.Series,
    split: DataSplit,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.Series,
    pd.Series,
]:
    """Apply a stored split to a feature matrix and target vector."""

    if not X.index.equals(y.index):
        raise MachineLearningError(
            "Feature and target indices do not match."
        )

    expected_indices = set(X.index)
    split_indices = set(split.train_indices) | set(split.test_indices)

    if expected_indices != split_indices:
        raise MachineLearningError(
            "The stored split does not match the modelling dataset."
        )

    overlapping = set(split.train_indices) & set(split.test_indices)

    if overlapping:
        raise MachineLearningError(
            "Training and test indices overlap."
        )

    X_train = X.loc[split.train_indices].copy()
    X_test = X.loc[split.test_indices].copy()
    y_train = y.loc[split.train_indices].copy()
    y_test = y.loc[split.test_indices].copy()

    return X_train, X_test, y_train, y_test
    
def write_split(
    split: DataSplit,
    research_ids: pd.Series,
    output_file: Path,
) -> Path:
    """
    Write a canonical train/test split using research identifiers.

    The output contains one row per student with the columns:

        research_id
        split

    The split values are either "train" or "test".
    """

    if research_ids.empty:
        raise MachineLearningError(
            "Cannot write a split for an empty identifier series."
        )

    if research_ids.isna().any():
        raise MachineLearningError(
            "Research identifiers contain missing values."
        )

    if research_ids.duplicated().any():
        raise MachineLearningError(
            "Research identifiers must be unique."
        )

    expected_indices = set(research_ids.index)

    split_indices = (
        set(split.train_indices)
        | set(split.test_indices)
    )

    if expected_indices != split_indices:
        raise MachineLearningError(
            "Research identifiers do not match the stored split indices."
        )

    split_membership = pd.Series(
        index=research_ids.index,
        dtype="object",
    )

    split_membership.loc[split.train_indices] = "train"
    split_membership.loc[split.test_indices] = "test"

    output = pd.DataFrame(
        {
            "research_id": research_ids,
            "split": split_membership,
        }
    )

    output = output.sort_values(
        by="research_id",
    ).reset_index(drop=True)

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.to_csv(
        output_file,
        index=False,
    )

    return output_file


    