"""
Input / Output functions for the Transition Analysis project.
"""

from pathlib import Path

import pandas as pd


# -----------------------------------------------------------------
# Project folders
# -----------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FOLDER = PROJECT_ROOT / "data"

DATA_FILE = DATA_FOLDER / "processed" / "transition_research.csv"


# -----------------------------------------------------------------

# Data Loading

# -----------------------------------------------------------------


def load_data() -> pd.DataFrame:
    """Load the governed research dataset for the legacy analysis modules."""

    df = pd.read_csv(DATA_FILE)

    legacy_column_names = {
        "course": "Course",
        "display_subject_code": "Display Subject Code",
        "subject_code": "Subject Code",
        "international_student": "International Student",
        "secondary_school_mathematics": "SOS",
        "historical_grade": "Grade",
        "current_subject": "Current 33130",
        "current_subject_pass": "Pass 33130",
        "has_previous_current_subject_attempt": "Has Previous 33130",
        "previous_current_subject_failure": "Previous 33130 Fail",
        "has_preparatory_subject": "Has 35010",
        "prior_preparatory_subject_failure": "Prior 35010 Fail",
        "prior_preparatory_subject_pass": "Prior 35010 Pass",
        "secondary_preparation_level": "SOS Level",
        "secondary_school_mark": "SOS Mark",
        "secondary_school_mark_band": "SOS Band",
        "current_outcome": "Current Outcome",
        "risk_index": "Risk Index",
    }

    return df.rename(columns=legacy_column_names)