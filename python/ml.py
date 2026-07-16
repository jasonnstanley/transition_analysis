"""
Machine-learning helper functions
for the Transition Analysis Toolkit.
"""

from sklearn.model_selection import train_test_split

from python.config import (
    RANDOM_STATE,
    TEST_SIZE,
)


def split_data(
    X,
    y,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
):
    """
    Create a reproducible stratified train/test split.

    Parameters
    ----------
    X
        Predictor variables.

    y
        Target variable.

    test_size
        Proportion of observations assigned to the test set.

    random_state
        Seed used to make the split reproducible.

    Returns
    -------
    tuple
        X_train, X_test, y_train, y_test
    """

    return train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )