"""
Pivot table functions.
"""

import pandas as pd


def pivot_counts(df, rows, columns):
    """
    Count pivot table.
    """
    return pd.crosstab(df[rows], df[columns])


def pivot_percent(df, rows, columns):
    """
    Row percentage pivot table.
    """
    table = pd.crosstab(df[rows], df[columns])

    return (
        table
        .div(table.sum(axis=1), axis=0)
        .mul(100)
        .round(2)
    )