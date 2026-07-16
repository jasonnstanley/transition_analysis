"""
LaTeX export functions.
"""


def dataframe_to_latex(df, caption, label):
    """
    Convert a DataFrame to a LaTeX table.
    """

    return df.to_latex(
        index=False,
        caption=caption,
        label=label,
        float_format="%.3f"
    )