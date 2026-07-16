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

DATA_FILE = DATA_FOLDER / "33130_autumn_2026.csv"


# -----------------------------------------------------------------

# Data Loading

# -----------------------------------------------------------------


def load_data():
  """
  Load the cleaned student-level dataset.
  
  Returns
  -------
  pandas.DataFrame
    The complete dataset.
  """
  
  return pd.read_csv(DATA_FILE)