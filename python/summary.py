"""
Summary functions for the Transition Analysis project.
"""

import pandas as pd


def cohort_size(df):
    """Return the number of students."""
    return len(df)


def pass_rate(df):
    """Return overall pass rate."""
    return df["Pass 33130"].mean()


def grade_counts(df):
    """Return counts of each final grade."""
    return df["Current Outcome"].value_counts()


def grade_distribution(df):
    """Return percentage distribution of each final grade."""
    return (
        df["Current Outcome"]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
    )


def count_by(df, field):
    """Return counts for any field."""
    return df[field].value_counts()


def distribution_by(df, field):
    """Return percentage distribution for any field."""
    return (
        df[field]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
    )
    
def pass_rate_by(df, field):
    """
    Return count, pass count, and pass rate grouped by a field.
    """
    grouped = df.groupby(field)["Pass 33130"]

    out = grouped.agg(
        Students="count",
        Passed="sum",
        PassRate="mean"
    )

    out["PassRate"] = (out["PassRate"] * 100).round(2)

    return out.sort_values("PassRate", ascending=False)