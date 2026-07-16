"""Prepare schema-safe modelling data for tree-based models."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from python.research_io import load_research_data


class TreeDataError(ValueError):
    """Raised when tree-model data cannot be prepared safely."""


@dataclass(frozen=True)
class TreeDataset:
    """Prepared feature matrix and outcome vector."""

    name: str
    X: pd.DataFrame
    y: pd.Series


TARGET_COLUMN = "current_subject_pass"

BASE_PREDICTORS = [
    "international_student",
    "has_previous_current_subject_attempt",
    "previous_current_subject_failure",
    "has_preparatory_subject",
    "prior_preparatory_subject_failure",
    "prior_preparatory_subject_pass",
    "secondary_preparation_level",
    "secondary_school_mark_band",
]

RISK_COLUMN = "risk_index"


def _normalise_binary_series(
    series: pd.Series,
    column_name: str,
) -> pd.Series:
    """
    Convert common binary representations to integers 0 and 1.

    Accepted values include:

    - Yes / No
    - Y / N
    - True / False
    - Pass / Fail
    - 1 / 0
    """

    if pd.api.types.is_bool_dtype(series):
        return series.astype(int)

    if pd.api.types.is_numeric_dtype(series):
        numeric = pd.to_numeric(series, errors="coerce")

        invalid_values = numeric.dropna().loc[
            ~numeric.dropna().isin([0, 1])
        ]

        if not invalid_values.empty:
            values = sorted(
                invalid_values.astype(str).unique().tolist()
            )

            raise TreeDataError(
                f"Column '{column_name}' contains non-binary "
                f"numeric values: {values}"
            )

        return numeric.astype("Int64")

    mapping = {
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

    cleaned = (
        series.astype("string")
        .str.strip()
        .str.lower()
    )

    converted = cleaned.map(mapping)

    invalid_mask = cleaned.notna() & converted.isna()

    if invalid_mask.any():
        invalid_values = sorted(
            cleaned.loc[invalid_mask].unique().tolist()
        )

        raise TreeDataError(
            f"Column '{column_name}' contains unrecognised "
            f"binary values: {invalid_values}"
        )

    return converted.astype("Int64")


def validate_modelling_columns(
    dataframe: pd.DataFrame,
) -> None:
    """Confirm that all required modelling columns are present."""

    required_columns = [
        TARGET_COLUMN,
        *BASE_PREDICTORS,
        RISK_COLUMN,
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        missing = ", ".join(missing_columns)

        raise TreeDataError(
            f"Research dataset is missing modelling columns: "
            f"{missing}"
        )


def prepare_target(
    dataframe: pd.DataFrame,
) -> pd.Series:
    """Prepare the binary outcome vector."""

    target = _normalise_binary_series(
        dataframe[TARGET_COLUMN],
        TARGET_COLUMN,
    )

    if target.isna().any():
        missing_count = int(target.isna().sum())

        raise TreeDataError(
            f"Target column '{TARGET_COLUMN}' contains "
            f"{missing_count} missing values."
        )

    return target.astype(int).rename(TARGET_COLUMN)


def prepare_features(
    dataframe: pd.DataFrame,
    include_risk_index: bool,
) -> pd.DataFrame:
    """Prepare the tree-model feature matrix."""

    predictor_columns = BASE_PREDICTORS.copy()

    if include_risk_index:
        predictor_columns.append(RISK_COLUMN)

    features = dataframe[predictor_columns].copy()

    binary_columns = [
        "international_student",
        "has_previous_current_subject_attempt",
        "previous_current_subject_failure",
        "has_preparatory_subject",
        "prior_preparatory_subject_failure",
        "prior_preparatory_subject_pass",
    ]

    for column in binary_columns:
        features[column] = _normalise_binary_series(
            features[column],
            column,
        )

    if include_risk_index:
        features[RISK_COLUMN] = pd.to_numeric(
            features[RISK_COLUMN],
            errors="coerce",
        )

    categorical_columns = [
        "secondary_preparation_level",
        "secondary_school_mark_band",
    ]

    for column in categorical_columns:
        features[column] = (
            features[column]
            .astype("string")
            .str.strip()
            .fillna("Missing")
        )

    numeric_columns = [
        column
        for column in features.columns
        if column not in categorical_columns
    ]

    for column in numeric_columns:
        if features[column].isna().any():
            missing_count = int(features[column].isna().sum())

            raise TreeDataError(
                f"Predictor '{column}' contains "
                f"{missing_count} missing values."
            )

        features[column] = pd.to_numeric(
            features[column],
            errors="raise",
        )

    encoded = pd.get_dummies(
        features,
        columns=categorical_columns,
        drop_first=False,
        dtype=int,
    )

    return encoded


def build_tree_datasets() -> tuple[TreeDataset, TreeDataset]:
    """
    Build tree-model datasets with and without the Risk Index.

    Returns
    -------
    tuple[TreeDataset, TreeDataset]
        Dataset without Risk Index, then dataset with Risk Index.
    """

    dataframe = load_research_data()

    validate_modelling_columns(dataframe)

    target = prepare_target(dataframe)

    without_risk = TreeDataset(
        name="Without Risk Index",
        X=prepare_features(
            dataframe,
            include_risk_index=False,
        ),
        y=target,
    )

    with_risk = TreeDataset(
        name="With Risk Index",
        X=prepare_features(
            dataframe,
            include_risk_index=True,
        ),
        y=target,
    )

    return without_risk, with_risk