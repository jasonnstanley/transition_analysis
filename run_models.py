from python.io import load_data
import python.models as models
import pandas as pd
from pathlib import Path
import python.latex as latex
import python.diagnostics as diagnostics    
from python.results import Results
import python.plots as plots

def main():
    
    OUTPUTS = Path("outputs")

    MODELS = OUTPUTS / "models"

    MODELS.mkdir(parents=True, exist_ok=True)
    
    df = load_data()

    # ==========================================================
    # Model 1 : Baseline
    # ==========================================================

    baseline = models.logistic_pass_model(df)

    print()
    print("Baseline Model")
    print("==============")
    print(baseline.summary())

    print()
    print("Odds Ratios")
    print("-----------")
    odds = models.odds_ratios(baseline)

    print(odds)

    odds.to_csv(
        MODELS / "baseline_odds.csv"
    )

    # ==========================================================
    # Model 2 : School Preparation
    # ==========================================================

    school = models.logistic_pass_model2(df)

    print()
    print("School Preparation Model")
    print("========================")
    print(school.summary())

    print()
    print("Odds Ratios")
    print("-----------")
    odds = models.odds_ratios(school)

    print(odds)

    odds.to_csv(
        MODELS / "school_odds.csv"
    )
    

    # ==========================================================
    # Model 3 : International Student
    # ==========================================================

    formula = """
    Q("Pass 33130")
    ~
    Q("Has 35010")
    + Q("Previous 33130 Fail")
    + C(Q("SOS Level"))
    + Q("International Student")
    """

    international = models.fit_model(df, formula)

    print()
    print("International Student Model")
    print("===========================")
    print(international.summary())

    print()
    print("Odds Ratios")
    print("-----------")
    odds = models.odds_ratios(international)

    print(odds)

    odds.to_csv(
        MODELS / "international_odds.csv"
    )

    # ==========================================================
    # Model 4 : Risk Index
    # ==========================================================

    formula = """
    Q("Pass 33130")
    ~
    Q("Risk Index")
    """

    risk = models.fit_model(df, formula)

    print()
    print("Risk Index Model")
    print("================")
    print(risk.summary())

    print()
    print("Odds Ratios")
    print("-----------")
    odds = models.odds_ratios(risk)

    print(odds)

    odds.to_csv(
        MODELS / "risk_odds.csv"
    )

    # ==========================================================
    # Model Comparison
    # ==========================================================

    comparison = pd.concat(
        [
            models.model_summary(baseline, "Baseline"),
            models.model_summary(school, "School Preparation"),
            models.model_summary(international, "International"),
            models.model_summary(risk, "Risk Index"),
        ],
        ignore_index=True
    )

    print()
    print("Model Comparison")
    print("================")
    print(comparison)
    
    # ==========================================================
    # Model Diagnostics
    # ==========================================================
    
    print()
    print("Model Diagnostics")
    print("=================")

    for name, model in [
        ("Baseline", baseline),
        ("School Preparation", school),
        ("International", international),
        ("Risk Index", risk),
    ]:
    
        auc = diagnostics.roc_auc(model, df, "Pass 33130")
        print(f"{name:20s} ROC AUC = {auc:.3f}")
    
    # ==========================================================
    # Model Confusion
    # ==========================================================
    
    
    print()
    print("Confusion Matrices")
    print("==================")

    for name, model in [
        ("Baseline", baseline),
        ("School Preparation", school),
        ("International", international),
        ("Risk Index", risk),
    ]:

        cm, acc = diagnostics.confusion(
            model,
            df,
            "Pass 33130"
        )

        print()
        print(name)

        print(cm)

        print(f"Accuracy = {acc:.3f}")
    
    # ==========================================================
    # Model Classification
    # ==========================================================
    
    print()
    print("Classification Metrics")
    print("======================")

    rows = []

    for name, model in [
        ("Baseline", baseline),
        ("School Preparation", school),
        ("International", international),
        ("Risk Index", risk),
    ]:

        metrics = diagnostics.classification_metrics(
            model,
            df,
            "Pass 33130"
        )

        metrics["Model"] = name

        rows.append(metrics)

    classification = pd.DataFrame(rows)

    print(classification)

 

    comparison.to_csv(
        MODELS / "model_comparison.csv",
        index=False
    )

    print()
    print("Saved: outputs/models/model_comparison.csv")

    tex = latex.dataframe_to_latex(
        comparison,
        caption="Comparison of logistic regression models.",
        label="tab:model-comparison"
    )

    with open(MODELS / "model_comparison.tex", "w", encoding="utf-8") as f:
        f.write(tex)

    print("Saved: outputs/models/model_comparison.tex")

    results = Results(df, "Pass 33130")

    results.add_model("Baseline", baseline)
    results.add_model("School Preparation", school)
    results.add_model("International", international)
    results.add_model("Risk Index", risk)

    print()
    print("Model Comparison")
    print("================")
    print(results.model_comparison())

    print()
    print("Classification Metrics")
    print("======================")
    print(results.classification_metrics())
    
    # ==========================================================   
    # Plots ROC curves
    # ==========================================================

    plots.roc_curves(
        results,
        "fig06_roc_curves.png"
    )
    
    
if __name__ == "__main__":
    main()