"""
Global configuration for the Transition Analysis Toolkit.
"""

from pathlib import Path

from python.version import __version__


# ----------------------------------------------------------------------
# Version
# ----------------------------------------------------------------------

VERSION = __version__


# ----------------------------------------------------------------------
# Project directories
# ----------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA = PROJECT_ROOT / "data"

RAW_DATA = DATA / "raw"
PROCESSED_DATA = DATA / "processed"

FIGURES = PROJECT_ROOT / "figures"
OUTPUTS = PROJECT_ROOT / "outputs"
REPORTS = PROJECT_ROOT / "reports"
PAPER = PROJECT_ROOT / "paper"
NOTEBOOKS = PROJECT_ROOT / "notebooks"

for directory in (
    FIGURES,
    OUTPUTS,
    REPORTS,
):
    directory.mkdir(exist_ok=True)


# ----------------------------------------------------------------------
# Machine Learning
# ----------------------------------------------------------------------

RANDOM_STATE = 42

TEST_SIZE = 0.30

N_ESTIMATORS = 500

TREE_MAX_DEPTH = 3


# ----------------------------------------------------------------------
# Plotting
# ----------------------------------------------------------------------

FIGURE_DPI = 300

FIGURE_SIZE = (10, 6)

TREE_FIGURE_SIZE = (18, 10)