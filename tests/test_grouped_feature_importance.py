"""Verify the canonical grouped feature-importance report."""

from pathlib import Path

import math

import pandas as pd


REPORT = Path("reports/grouped_feature_importance.csv")

EXPECTED_COLUMNS = [
    "group_rank",
    "feature_group",
    "Decision Tree — With Risk",
    "Decision Tree — Without Risk",
    "Random Forest — With Risk",
    "Random Forest — Without Risk",
    "average_across_models",
]

EXPECTED_GROUPS = [
    "Secondary mathematics preparation",
    "Composite risk measure",
    "Preparatory mathematics",
    "Previous university performance",
    "Secondary school achievement",
    "Student characteristics",
]

EXPECTED_AVERAGES = {
    "Secondary mathematics preparation": 0.275538,
    "Composite risk measure": 0.238111,
    "Preparatory mathematics": 0.232044,
    "Previous university performance": 0.108996,
    "Secondary school achievement": 0.105827,
    "Student characteristics": 0.039484,
}


def test_grouped_feature_importance_report() -> None:
    """Verify report structure, ordering, and canonical grouped results."""

    assert REPORT.exists(), f"Missing report: {REPORT}"

    data = pd.read_csv(REPORT)

    assert list(data.columns) == EXPECTED_COLUMNS, (
        "Unexpected grouped feature-importance columns.\n"
        f"Expected: {EXPECTED_COLUMNS}\n"
        f"Actual:   {list(data.columns)}"
    )

    assert len(data) == 6, (
        f"Expected 6 feature groups, found {len(data)}."
    )

    assert data["group_rank"].tolist() == [1, 2, 3, 4, 5, 6], (
        "Feature-group ranks are not the canonical sequence 1–6."
    )

    assert data["feature_group"].tolist() == EXPECTED_GROUPS, (
        "Feature groups or their ordering have changed."
    )

    model_columns = EXPECTED_COLUMNS[2:6]

    for column in model_columns:
        assert data[column].between(0, 1).all(), (
            f"Feature importance values in {column!r} fall outside [0, 1]."
        )

        total = data[column].sum()

        assert math.isclose(total, 1.0, abs_tol=2e-6), (
            f"Feature importances in {column!r} sum to {total}, not 1."
        )

    for feature_group, expected_average in EXPECTED_AVERAGES.items():
        row = data.loc[data["feature_group"] == feature_group]

        assert len(row) == 1, (
            f"Expected exactly one row for {feature_group!r}."
        )

        actual_average = float(row.iloc[0]["average_across_models"])

        assert math.isclose(
            actual_average,
            expected_average,
            abs_tol=1e-6,
        ), (
            f"{feature_group!r}: expected average importance "
            f"{expected_average}, found {actual_average}."
        )

    calculated_averages = data[model_columns].mean(axis=1)

    assert all(
        math.isclose(actual, calculated, abs_tol=1e-6)
        for actual, calculated in zip(
            data["average_across_models"],
            calculated_averages,
        )
    ), "average_across_models does not match the four model columns."


def main() -> None:
    """Run grouped feature-importance verification as a standalone script."""

    test_grouped_feature_importance_report()

    print("Grouped feature-importance report verified.")
    print("All six feature groups match the canonical results.")


if __name__ == "__main__":
    main()