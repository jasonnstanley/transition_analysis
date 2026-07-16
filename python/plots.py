"""
Plotting functions for the Transition Analysis project.
"""

from pathlib import Path
import matplotlib.pyplot as plt
from sklearn.metrics import RocCurveDisplay

FIGURES = Path("figures")
FIGURES.mkdir(exist_ok=True)


def plot_roc_curves(results, output_dir="outputs/plots"):
    """
    Plot ROC curves for all fitted classification models
    stored in the Results object.
    """

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6))

    for model_name, item in results.models.items():
        model = item["model"]
        X_test = item["X_test"]
        y_test = item["y_test"]

        if hasattr(model, "predict_proba"):
            RocCurveDisplay.from_estimator(
                model,
                X_test,
                y_test,
                ax=ax,
                name=model_name
            )

    ax.set_title("ROC Curves for Classification Models")
    ax.grid(True)

    filename = output_path / "roc_curves.png"
    fig.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return filename

def bar_chart(series, title, ylabel, filename):
    """
    Draw and save a bar chart from a pandas Series.
    """

    plt.figure(figsize=(10, 6))

    series.plot(
        kind="bar",
        width=0.8
    )

    plt.title(title)

    plt.xlabel("")

    plt.ylabel(ylabel)
    
    plt.xticks(rotation=0)
    
    plt.grid(axis="y", alpha=0.3)
    
    plt.ylim(bottom=0)
    
    plt.tight_layout()

    outfile = FIGURES / filename

    plt.savefig(outfile, dpi=300)

    plt.close()

    print(f"Saved {outfile}")
    
def roc_curves(results, filename):
    """
    Plot ROC curves for all models in a Results object.
    """

    plt.figure(figsize=(8, 8))

    for name, model in results.models:
        fpr, tpr, thresholds = results.roc_curve_data(model)

        auc = results.roc_auc(model)

        plt.plot(
            fpr,
            tpr,
            label=f"{name} (AUC = {auc:.3f})"
        )

    plt.plot(
        [0, 1],
        [0, 1],
        linestyle="--",
        label="Chance"
    )

    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curves")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    outfile = FIGURES / filename
    plt.savefig(outfile, dpi=300)
    plt.close()

    print(f"Saved {outfile}")    