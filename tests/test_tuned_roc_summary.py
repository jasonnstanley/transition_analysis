"""Verify the published tuned ROC summary."""

from pathlib import Path

import math
import pandas as pd


ROC_SUMMARY = Path("reports/tuned_roc_summary.csv")

EXPECTED = {
    ("Decision Tree — With Risk", "With Risk Index"):
        (0.707238, 0.766375),

    ("Random Forest — Without Risk", "Without Risk Index"):
        (0.710075, 0.760306),

    ("Random Forest — With Risk", "With Risk Index"):
        (0.709462, 0.759947),

    ("Decision Tree — Without Risk", "Without Risk Index"):
        (0.699386, 0.755710),
}


def main():

    assert ROC_SUMMARY.exists(), (
        f"Missing report: {ROC_SUMMARY}"
    )

    df = pd.read_csv(ROC_SUMMARY)

    assert len(df) == 4, (
        f"Expected 4 models, found {len(df)}."
    )

    for _, row in df.iterrows():

        key = (row["model"], row["dataset"])

        assert key in EXPECTED, (
            f"Unexpected model: {key}"
        )

        expected_cv, expected_test = EXPECTED[key]

        assert math.isclose(
            row["cv_roc_auc"],
            expected_cv,
            abs_tol=1e-6,
        ), (
            f"{key} CV ROC mismatch."
        )

        assert math.isclose(
            row["roc_auc"],
            expected_test,
            abs_tol=1e-6,
        ), (
            f"{key} Test ROC mismatch."
        )

        assert row["test_rows"] == 295
        assert row["test_passes"] == 236
        assert row["test_non_passes"] == 59

    print("Published tuned ROC summary verified.")
    print("All four tuned models match the canonical results.")


if __name__ == "__main__":
    main()