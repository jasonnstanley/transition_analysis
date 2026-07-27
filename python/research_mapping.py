"""
Mapping between research questions and generated outputs.
"""

from python.research_models import ResearchEvidence


RESEARCH_MAPPING = {
    "RQ1": ResearchEvidence(
        tables=[
            "tuned_roc_summary.tex",
            "grouped_feature_importance.tex",
            "feature_rankings.tex",
        ],
        figures=[
            "fig_tuned_tree_roc_comparison.png",
            "fig_tuned_feature_importance_grouped.png",
        ],
        narrative=[
            "model_interpretation.tex",
        ],
    ),

    "RQ2": ResearchEvidence(),

    "RQ3": ResearchEvidence(),
}