"""
Logging utilities for the Transition Analysis Toolkit.
"""

import logging
from datetime import datetime

from python.config import PROJECT_ROOT

LOGS = PROJECT_ROOT / "logs"
LOGS.mkdir(exist_ok=True)


def create_logger(name="transition_analysis"):
    """
    Create a project logger.
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    logfile = LOGS / f"analysis_{timestamp}.log"

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s  %(levelname)-8s %(message)s"
    )

    file_handler = logging.FileHandler(logfile)

    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("=" * 60)
    logger.info("Transition Analysis Toolkit")
    logger.info("=" * 60)

    return logger