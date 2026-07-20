"""
Master analysis runner for the Transition Analysis Toolkit.
"""

import subprocess
import sys
from time import perf_counter

from python.config import PROJECT_ROOT
from python.logger import create_logger
from python.version import version_string


SCRIPTS = [
    "run_summary.py",
    "run_report.py",
    "run_tables.py",
    "run_plots.py",
    "run_statistics.py",
    "run_models.py",
    "run_trees.py",
    "run_forests.py",
    "run_ml_comparison.py",
]


def run(script_name, logger):
    """
    Run one analysis script using the active Python interpreter.
    """

    script_path = PROJECT_ROOT / script_name

    if not script_path.exists():
        raise FileNotFoundError(
            f"Analysis script not found: {script_path}"
        )

    logger.info("Starting %s", script_name)

    start_time = perf_counter()

    subprocess.run(
        [sys.executable, str(script_path)],
        check=True,
        cwd=PROJECT_ROOT,
    )

    elapsed = perf_counter() - start_time

    logger.info(
        "Completed %s in %.2f seconds",
        script_name,
        elapsed,
    )


def main():
    """
    Run the complete analysis pipeline.
    """

    logger = create_logger()

    pipeline_start = perf_counter()

    logger.info(version_string())
    logger.info("Project root: %s", PROJECT_ROOT)

    try:
        for script_name in SCRIPTS:
            run(script_name, logger)

    except subprocess.CalledProcessError as error:
        logger.exception(
            "Pipeline failed while running %s",
            error.cmd,
        )
        raise

    except Exception:
        logger.exception("Pipeline failed.")
        raise

    elapsed = perf_counter() - pipeline_start

    logger.info(
        "Analysis complete in %.2f seconds.",
        elapsed,
    )


if __name__ == "__main__":
    main()