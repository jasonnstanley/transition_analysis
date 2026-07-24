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

from python.config import (
    REPORTS,
    REPORT_DATA,
    REPORT_TABLES,
    FIGURES,
)


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
FEATURE_LABELS = {
    "risk_index": "Composite risk index",
    "has_previous_current_subject_attempt":
        "Previous attempt at current subject",
    "previous_current_subject_failure":
        "Previous failure in current subject",
    "has_preparatory_subject":
        "Prior preparatory mathematics",
    "prior_preparatory_subject_failure":
        "Previous preparatory mathematics failure",
    "prior_preparatory_subject_pass":
        "Previous preparatory mathematics pass",
    "international_student":
        "International student",
    "secondary_preparation_level_Advanced":
        "Secondary mathematics: Advanced",
    "secondary_preparation_level_Ext1":
        "Secondary mathematics: Extension 1",
    "secondary_preparation_level_Ext2":
        "Secondary mathematics: Extension 2",
    "secondary_preparation_level_Other":
        "Secondary mathematics: Other",
    "secondary_preparation_level_Standard":
        "Secondary mathematics: Standard",
    "secondary_school_mark_band_<70":
        "Secondary school mark below 70",
    "secondary_school_mark_band_70-79":
        "Secondary school mark 70–79",
    "secondary_school_mark_band_80-89":
        "Secondary school mark 80–89",
    "secondary_school_mark_band_90+":
        "Secondary school mark 90 or above",
}

GROUP_INTERPRETATION = {
    "Secondary mathematics preparation":
        "This suggests that prior secondary mathematics preparation was the strongest and most consistent predictor of success across the tuned models.",

    "Composite risk measure":
        "The composite risk measure captured multiple sources of prior academic risk, providing substantial predictive power when included.",

    "Preparatory mathematics":
        "Preparatory mathematics pathways contributed strongly, supporting their role in assisting students entering first-year mathematics.",

    "Previous university performance":
        "Previous university mathematics performance provided additional information beyond secondary school preparation.",

    "Secondary school achievement":
        "Overall secondary school achievement remained informative but contributed less than mathematics-specific preparation.",

    "Student characteristics":
        "Student demographic characteristics contributed comparatively little to prediction within these models."
}

NUMBER_WORDS = {
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
}

def format_count(value: int) -> str:
    return NUMBER_WORDS.get(value, str(value))

def load_feature_importance() -> pd.DataFrame:
    """
    Load the long-format tuned feature-importance table.
    """

    filename = REPORT_DATA / "tuned_feature_importance_long.csv"

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

def build_interpretation_narrative(
    grouped_summary: pd.DataFrame,
) -> str:
    """
    Generate a concise research interpretation from grouped importance.
    """

    ranked = grouped_summary.sort_values(
        "average_across_models",
        ascending=False,
    ).reset_index(drop=True)
    
    if len(ranked) < 4:
        raise ValueError(
            "At least four feature groups are required to "
            "generate the interpretation narrative."
        )
    
    first = ranked.iloc[0]["feature_group"]
    second = ranked.iloc[1]["feature_group"]
    third = ranked.iloc[2]["feature_group"]
    lowest = ranked.iloc[-1]["feature_group"]

    first_value = ranked.iloc[0]["average_across_models"]
    second_value = ranked.iloc[1]["average_across_models"]
    third_value = ranked.iloc[2]["average_across_models"]
    
    top_three_total = first_value + second_value + third_value
    
    consistency = (
        grouped_summary.drop(columns=["group_rank", "feature_group", "average_across_models"])
        .gt(0)
        .sum(axis=1)
    )

    first_models = int(consistency.iloc[0])
    second_models = int(consistency.iloc[1])
    third_models = int(consistency.iloc[2])
    
    educational_interpretation = GROUP_INTERPRETATION.get(first, "")
    
    model_columns = [
    column
    for column in grouped_summary.columns
        if column not in {
                "group_rank",
                "feature_group",
                "average_across_models",
            }
    ]

    model_count = len(model_columns)
    
    return (
        f"Across the tuned tree-based models, {first.lower()} "
        f"emerged as the most influential predictor group "
        f"(mean importance = {format_importance(first_value)}). "
        f"This was followed by the {second.lower()} "
        f"({second_value:.3f}) and {third.lower()} "
        f"({third_value:.3f}). "
        f"Together, these three groups accounted for "
        f"{format_percentage(top_three_total)} of the average feature "
        f"importance across the tuned models. "
        f"{first.capitalize()} remained influential across "
        f"all {format_count(first_models)} models, whereas the "
        f"{second.lower()} contributed strongly but "
        f"appeared in {format_count(second_models)} of the {format_count(model_count)} models. "
        f"In contrast, {lowest.lower()} made the smallest "
        f"average contribution."
        f" {educational_interpretation}"
    )

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

    csv_file = REPORT_DATA / csv_name
    tex_file = REPORT_TABLES / tex_name

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
    
    plot_df["feature_label"] = (
        plot_df["feature"]
            .map(FEATURE_LABELS)
            .fillna(plot_df["feature"])
    )
    
    plot_df = plot_df.sort_values(
        "included_model_average",
        ascending=True,
    )

    fig, ax = plt.subplots(figsize=(10, 7))

    ax.barh(
        plot_df["feature_label"],
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
    
def format_importance(value: float) -> str:
    """Format feature importance values for publication."""
    return f"{value:.3f}"


def format_percentage(value: float) -> str:
    """Format proportions as percentages for publication."""
    return f"{value:.1%}"
    
    
    
    
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
    
    interpretation_narrative = build_interpretation_narrative(
        grouped_summary
    )

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
    print()
    print("-" * 72)
    print("Interpretation narrative")
    print("-" * 72)
    print()
    print(interpretation_narrative)
    markdown_report = REPORTS / "model_interpretation.md"

    markdown_report.write_text(
        "\n".join(
            [
                 "# Model Interpretation",
                 "",
                 "## Cross-model interpretation",
                 "",
                 interpretation_narrative,
                 "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Markdown report: {markdown_report}")
    
    latex_report = REPORTS / "model_interpretation.tex"

    latex_report.write_text(
        "\n".join(
            [
#                r"\section{Model Interpretation}",
                "",
                interpretation_narrative.replace("%", r"\%"),
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"LaTeX report: {latex_report}")
    
    rankings_for_report = rankings.copy()

    rankings_for_report["feature"] = (
        rankings_for_report["feature"]
        .map(FEATURE_LABELS)
        .fillna(rankings_for_report["feature"])
    )

    save_dataframe(
        rankings_for_report,
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