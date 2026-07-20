"""Verify the legacy analysis data interface."""

from __future__ import annotations

from python.io import load_data


def test_legacy_analysis_column_interface() -> None:
    """The governed dataset must expose the columns expected by legacy models."""

    df = load_data()

    expected_columns = {
        "Pass 33130",
        "Has 35010",
        "Previous 33130 Fail",
        "Has Previous 33130",
        "Prior 35010 Fail",
        "Prior 35010 Pass",
        "SOS Level",
        "SOS Mark",
        "SOS Band",
        "Risk Index",
    }

    missing_columns = expected_columns - set(df.columns)

    assert not missing_columns, (
        "Legacy analysis interface is missing columns: "
        f"{sorted(missing_columns)}"
    )

    assert len(df) == 1473