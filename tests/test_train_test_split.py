"""Verify the canonical train/test split used by Python and R."""

from pathlib import Path

import pandas as pd


RESEARCH_DATA = Path("data/processed/transition_research.csv")
SPLIT_DATA = Path("data/processed/train_test_split.csv")

EXPECTED_TOTAL = 1473
EXPECTED_TRAIN = 1178
EXPECTED_TEST = 295

EXPECTED_OUTCOME_COUNTS = {
    "train": {0: 236, 1: 942},
    "test": {0: 59, 1: 236},
}


def test_canonical_train_test_split() -> None:
    """Verify split membership, counts, identifiers, and outcome balance."""

    assert RESEARCH_DATA.exists(), f"Missing file: {RESEARCH_DATA}"
    assert SPLIT_DATA.exists(), f"Missing file: {SPLIT_DATA}"

    research = pd.read_csv(RESEARCH_DATA)
    split = pd.read_csv(SPLIT_DATA)

    assert list(split.columns) == ["research_id", "split"], (
        "Unexpected train/test split columns: "
        f"{list(split.columns)}"
    )

    assert len(research) == EXPECTED_TOTAL, (
        f"Expected {EXPECTED_TOTAL} research rows, found {len(research)}."
    )

    assert len(split) == EXPECTED_TOTAL, (
        f"Expected {EXPECTED_TOTAL} split rows, found {len(split)}."
    )

    assert split["research_id"].notna().all(), (
        "The split file contains missing research IDs."
    )

    assert split["research_id"].is_unique, (
        "Each research ID must occur exactly once in the split file."
    )

    valid_labels = {"train", "test"}
    actual_labels = set(split["split"].dropna().unique())

    assert actual_labels == valid_labels, (
        f"Expected split labels {sorted(valid_labels)}, "
        f"found {sorted(actual_labels)}."
    )

    split_counts = split["split"].value_counts().to_dict()

    assert split_counts.get("train") == EXPECTED_TRAIN, (
        f"Expected {EXPECTED_TRAIN} training rows, "
        f"found {split_counts.get('train')}."
    )

    assert split_counts.get("test") == EXPECTED_TEST, (
        f"Expected {EXPECTED_TEST} test rows, "
        f"found {split_counts.get('test')}."
    )

    research_ids = set(research["research_id"])
    split_ids = set(split["research_id"])

    missing_from_split = research_ids - split_ids
    unknown_in_split = split_ids - research_ids

    assert not missing_from_split, (
        f"{len(missing_from_split)} research IDs are missing from the split file."
    )

    assert not unknown_in_split, (
        f"{len(unknown_in_split)} split IDs are absent from the research dataset."
    )

    merged = research[
        ["research_id", "current_subject_pass"]
    ].merge(
        split,
        on="research_id",
        how="inner",
        validate="one_to_one",
    )

    for split_name, expected_counts in EXPECTED_OUTCOME_COUNTS.items():
        observed = (
            merged.loc[
                merged["split"] == split_name,
                "current_subject_pass",
            ]
            .value_counts()
            .to_dict()
        )

        for outcome, expected_count in expected_counts.items():
            actual_count = observed.get(outcome, 0)

            assert actual_count == expected_count, (
                f"{split_name!r} outcome {outcome}: "
                f"expected {expected_count}, found {actual_count}."
            )


def main() -> None:
    """Run split verification as a standalone script."""

    test_canonical_train_test_split()

    split = pd.read_csv(SPLIT_DATA)
    split_counts = split["split"].value_counts().to_dict()

    print("Canonical train/test split verified.")
    print(f"Total rows:    {len(split)}")
    print(f"Training rows: {split_counts['train']}")
    print(f"Test rows:     {split_counts['test']}")
    print("Outcome distributions match the verified Python/R split.")


if __name__ == "__main__":
    main()