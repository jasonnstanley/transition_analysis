"""Safety and integrity checks for the public research datasets."""

from pathlib import Path

import pandas as pd


RESEARCH_DATA = Path("data/processed/transition_research.csv")
SPLIT_DATA = Path("data/processed/train_test_split.csv")

FORBIDDEN_COLUMNS = {
    "student_code",
    "last_name",
    "preferred_name",
    "email_address",
}

REQUIRED_RESEARCH_COLUMNS = {
    "research_id",
    "current_subject_pass",
    "current_outcome",
    "risk_index",
}


def main() -> None:
    """Verify that public datasets are de-identified and internally valid."""

    assert RESEARCH_DATA.exists(), f"Missing file: {RESEARCH_DATA}"
    assert SPLIT_DATA.exists(), f"Missing file: {SPLIT_DATA}"

    research = pd.read_csv(RESEARCH_DATA)
    split = pd.read_csv(SPLIT_DATA)

    research_columns = set(research.columns)

    exposed_columns = FORBIDDEN_COLUMNS.intersection(research_columns)
    assert not exposed_columns, (
        "Identifying columns found in public research data: "
        f"{sorted(exposed_columns)}"
    )

    missing_columns = REQUIRED_RESEARCH_COLUMNS.difference(research_columns)
    assert not missing_columns, (
        "Required research columns are missing: "
        f"{sorted(missing_columns)}"
    )

    assert research["research_id"].notna().all(), (
        "research_id contains missing values."
    )

    assert research["research_id"].is_unique, (
        "research_id values are not unique."
    )

    assert len(research) > 0, "Research dataset is empty."
    assert len(split) > 0, "Train/test split dataset is empty."

    print("Public research data checks passed.")
    print(f"Research rows: {len(research)}")
    print(f"Split rows:    {len(split)}")


if __name__ == "__main__":
    main()