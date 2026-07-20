"""
interpret_models.py

Interpretation of tuned tree models.

Produces:

    • Ranked feature importance tables
    • Grouped importance summaries
    • Publication-ready LaTeX tables
    • Markdown interpretation report
"""
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from python.report_utils import (
    save_dataframe_reports,
    validate_columns,
)

from python.config import REPORTS, FIGURES


FEATURE_GROUPS = {
    "risk_index": "Composite risk measure",

    "has_previous_current_subject_attempt":
        "Previous university performance",

    "previous_current_subject_failure":
        "Previous university performance",

    "has_preparatory_subject":
        "Preparatory mathematics",

    "prior_preparatory_subject_failure":
        "Preparatory mathematics",

    "prior_preparatory_subject_pass":
        "Preparatory mathematics",

    "international_student":
        "Student characteristics",

    "secondary_preparation_level_Advanced":
        "Secondary mathematics preparation",

    "secondary_preparation_level_Ext1":
        "Secondary mathematics preparation",

    "secondary_preparation_level_Ext2":
        "Secondary mathematics preparation",

    "secondary_preparation_level_Other":
        "Secondary mathematics preparation",

    "secondary_preparation_level_Standard":
        "Secondary mathematics preparation",

    "secondary_school_mark_band_<70":
        "Secondary school achievement",

    "secondary_school_mark_band_70-79":
        "Secondary school achievement",

    "secondary_school_mark_band_80-89":
        "Secondary school achievement",

    "secondary_school_mark_band_90+":
        "Secondary school achievement",
}

def load_feature_importance() -> pd.DataFrame:
    """
    Load the long-format tuned feature-importance table.
    """

    filename = REPORTS / "tuned_feature_importance_long.csv"

    if not filename.exists():
        raise FileNotFoundError(
            f"Feature-importance file not found:\n{filename}"
        )

    return pd.read_csv(filename)
    
def build_feature_rankings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a cross-model feature-importance table.

    Two averages are reported:

    all_model_average
        Mean across all fitted models. Features unavailable to a model are
        represented as zero.

    included_model_average
        Mean only across models in which the feature was available.

    The distinction is important for derived predictors such as risk_index,
    which is intentionally absent from the without-risk models.
    """

    validate_columns(
        df,
        {
            "model",
            "feature",
            "importance",
        },
        context="Feature importance table",
    )

    

    model_names = sorted(df["model"].unique())

    # Preserve missing feature/model combinations as NaN initially.
    importance_wide = df.pivot_table(
        index="feature",
        columns="model",
        values="importance",
        aggfunc="sum",
    )

    # Number of models in which each feature was actually present.
    models_included = importance_wide.notna().sum(axis=1)

    # Average only over models containing the feature.
    included_model_average = importance_wide.mean(
        axis=1,
        skipna=True,
    )

    # Average across every model, treating absence as zero.
    all_model_average = (
        importance_wide.reindex(columns=model_names)
        .fillna(0.0)
        .mean(axis=1)
    )

    rankings = (
        importance_wide
        .reindex(columns=model_names)
        .fillna(0.0)
        .reset_index()
    )

    rankings["models_included"] = (
        rankings["feature"]
        .map(models_included)
        .astype(int)
    )

    rankings["included_model_average"] = (
        rankings["feature"]
        .map(included_model_average)
    )

    rankings["all_model_average"] = (
        rankings["feature"]
        .map(all_model_average)
    )

    rankings = rankings.sort_values(
        by=[
            "included_model_average",
            "all_model_average",
        ],
        ascending=False,
    ).reset_index(drop=True)

    rankings.insert(
        0,
        "overall_rank",
        range(1, len(rankings) + 1),
    )

    return rankings
    
def build_grouped_importance(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Aggregate feature importance into substantive research groups.

    Dummy-coded features belonging to the same conceptual variable are
    summed within each model.

    Importance values within each fitted model should sum to approximately
    one, so grouped values represent the proportion of model importance
    attributed to each research theme.
    """

    validate_columns(
        df,
        {
            "model",
            "model_type",
            "dataset",
            "feature",
            "importance",
        },
        context="Grouped feature importance",
    )

    

    grouped = df.copy()

    grouped["feature_group"] = grouped["feature"].map(
        FEATURE_GROUPS
    )

    unmapped_features = sorted(
        grouped.loc[
            grouped["feature_group"].isna(),
            "feature",
        ].unique()
    )

    if unmapped_features:
        unmapped_text = "\n".join(
            f"  - {feature}"
            for feature in unmapped_features
        )

        raise ValueError(
            "The following features have not been assigned to a "
            f"research group:\n{unmapped_text}"
        )

    grouped = (
        grouped.groupby(
            [
                "model",
                "model_type",
                "dataset",
                "feature_group",
            ],
            as_index=False,
        )["importance"]
        .sum()
    )

    grouped["group_rank"] = (
        grouped.groupby("model")["importance"]
        .rank(
            method="dense",
            ascending=False,
        )
        .astype(int)
    )

    grouped = grouped.sort_values(
        by=[
            "model",
            "group_rank",
            "feature_group",
        ]
    ).reset_index(drop=True)

    return grouped    
    
def build_grouped_summary(
    grouped_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create a wide comparison of grouped feature importance.

    Missing groups are represented as zero because the group was unavailable
    in that model, such as the composite risk measure in without-risk models.
    """

    summary = (
        grouped_df.pivot_table(
            index="feature_group",
            columns="model",
            values="importance",
            aggfunc="sum",
            fill_value=0.0,
        )
        .reset_index()
    )

    model_columns = [
        column
        for column in summary.columns
        if column != "feature_group"
    ]

    summary["average_across_models"] = (
        summary[model_columns].mean(axis=1)
    )

    summary = summary.sort_values(
        by="average_across_models",
        ascending=False,
    ).reset_index(drop=True)

    summary.insert(
        0,
        "group_rank",
        range(1, len(summary) + 1),
    )

    return summary    

def save_dataframe(
    df: pd.DataFrame,
    csv_name: str,
    tex_name: str,
    float_format: str = "%.4f",
    tex_columns: list[str] | None = None,
    tex_column_names: dict[str, str] | None = None,
) -> None:
    """
    Save the complete dataframe as CSV and a publication-oriented
    selection of columns as LaTeX.
    """

    csv_file = REPORTS / csv_name
    tex_file = REPORTS / tex_name

    # Preserve the complete machine-readable report.
    df.to_csv(
        csv_file,
        index=False,
    )

    # Optionally restrict and rename columns for the paper table.
    tex_df = df.copy()

    if tex_columns is not None:
        tex_df = tex_df.loc[:, tex_columns].copy()

    if tex_column_names is not None:
        tex_df = tex_df.rename(columns=tex_column_names)

    latex = tex_df.to_latex(
        index=False,
        float_format=float_format,
        escape=True,
        longtable=False,
    )

    tex_file.write_text(
        latex,
        encoding="utf-8",
    )

    print(f"CSV : {csv_file}")
    print(f"TEX : {tex_file}")

def plot_individual_feature_importance(
    rankings: pd.DataFrame,
) -> Path:
    """
    Plot the leading individual predictors across tuned models.
    """

    plot_df = rankings.head(10).copy()

    plot_df = plot_df.sort_values(
        "included_model_average",
        ascending=True,
    )

    fig, ax = plt.subplots(figsize=(10, 7))

    ax.barh(
        plot_df["feature"],
        plot_df["included_model_average"],
    )

    ax.set_xlabel("Mean feature importance")
    ax.set_ylabel("")
    ax.set_title(
        "Leading predictors across tuned tree-based models"
    )

    fig.tight_layout()

    output_path = (
        FIGURES
        / "fig_tuned_feature_importance_individual.png"
    )

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)

    return output_path

def plot_grouped_feature_importance(
    grouped_summary: pd.DataFrame,
) -> Path:
    """
    Plot grouped feature importance across tuned models.
    """

    plot_df = grouped_summary.sort_values(
        "average_across_models",
        ascending=True,
    )

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.barh(
        plot_df["feature_group"],
        plot_df["average_across_models"],
    )

    ax.set_xlabel("Mean grouped importance")
    ax.set_ylabel("")
    ax.set_title(
        "Predictive importance by research theme"
    )

    fig.tight_layout()

    output_path = (
        FIGURES
        / "fig_tuned_feature_importance_grouped.png"
    )

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)

    return output_path
    
    
    
    
    
    
def main() -> None:
    print("=" * 72)
    print("Model Interpretation")
    print("=" * 72)

    df = load_feature_importance()

    print()
    print(df.head())

    print()
    print(f"Rows      : {len(df)}")
    print(f"Models    : {df['model'].nunique()}")
    print(f"Features  : {df['feature'].nunique()}")
    print(f"Datasets  : {df['dataset'].nunique()}")
    
    
    rankings = build_feature_rankings(df)

    print()
    print("-" * 72)
    print("Cross-model feature rankings")
    print("-" * 72)
    print()
    print(rankings.head(10).to_string(index=False))
    
    grouped = build_grouped_importance(df)
    grouped_summary = build_grouped_summary(grouped)

    print()
    print("-" * 72)
    print("Grouped feature importance by model")
    print("-" * 72)
    print()
    print(grouped.to_string(index=False))

    print()
    print("-" * 72)
    print("Cross-model grouped summary")
    print("-" * 72)
    print()
    print(grouped_summary.to_string(index=False))
    


    save_dataframe(
        rankings,
            "feature_rankings.csv",
            "feature_rankings.tex",
        tex_columns=[
            "overall_rank",
            "feature",
            "models_included",
            "included_model_average",
        ],
        tex_column_names={
            "overall_rank": "Rank",
            "feature": "Feature",
            "models_included": "Models",
            "included_model_average": "Mean importance",
        },
    )

    save_dataframe(
        grouped_summary,
        "grouped_feature_importance.csv",
        "grouped_feature_importance.tex",
        tex_columns=[
            "group_rank",
            "feature_group",
            "average_across_models",
        ],
        tex_column_names={
            "group_rank": "Rank",
            "feature_group": "Research theme",
            "average_across_models": "Mean importance",
        },
    )


    individual_figure = plot_individual_feature_importance(
        rankings
    )

    grouped_figure = plot_grouped_feature_importance(
        grouped_summary
    )

    print(f"Individual figure:     {individual_figure}")
    print(f"Grouped figure:        {grouped_figure}")
    
if __name__ == "__main__":
    main()