"""
Statistical tests for Transition Analysis.
"""

from scipy.stats import chi2_contingency
import pandas as pd
import numpy as np

def chi_square(df, rows, columns):
    """
    Chi-square test of independence.
    """

    table = pd.crosstab(df[rows], df[columns])

    chi2, p, dof, expected = chi2_contingency(table)

    return {
        "chi2": chi2,
        "p": p,
        "dof": dof,
        "observed": table,
        "expected": expected,
    }
    
    
def cramers_v(df, rows, columns):
    """
    Calculate Cramér's V for the association between two categorical variables.
    """

    table = pd.crosstab(df[rows], df[columns])

    chi2, p, dof, expected = chi2_contingency(table)

    n = table.to_numpy().sum()

    r, c = table.shape

    return np.sqrt(chi2 / (n * (min(r - 1, c - 1))))