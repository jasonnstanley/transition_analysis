"""
Random forest models for the Transition Analysis Toolkit.
"""

import matplotlib.pyplot as plt
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from python.config import (
    FIGURE_DPI,
    FIGURE_SIZE,
    FIGURES,
    N_ESTIMATORS,
    RANDOM_STATE,
)


def fit_random_forest(
    X_train,
    y_train,
    n_estimators=N_ESTIMATORS,
    max_depth=None,
    random_state=RANDOM_STATE,
):
    """
    Fit a balanced Random Forest classifier.
    """

    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state,
        class_weight="balanced",
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    return model


def evaluate_random_forest(model, X_test, y_test):
    """
    Evaluate a fitted Random Forest on test data.
    """

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    return {
        "Accuracy": accuracy_score(y_test, predictions),
        "Balanced Accuracy": balanced_accuracy_score(
            y_test,
            predictions,
        ),
        "Precision": precision_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "Recall": recall_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "F1": f1_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "ROC AUC": roc_auc_score(
            y_test,
            probabilities,
        ),
    }


def feature_importance_table(model, feature_names):
    """
    Return Random Forest feature importances.
    """

    table = pd.DataFrame(
        {
            "Feature": list(feature_names),
            "Importance": model.feature_importances_,
        }
    )

    return table.sort_values(
        by="Importance",
        ascending=False,
    ).reset_index(drop=True)


def save_feature_importance_plot(
    importance_table,
    filename,
    title="Random Forest Feature Importance",
):
    """
    Save a horizontal feature-importance chart.
    """

    plot_data = importance_table.sort_values(
        by="Importance",
        ascending=True,
    )

    figure, axis = plt.subplots(figsize=FIGURE_SIZE)

    axis.barh(
        plot_data["Feature"],
        plot_data["Importance"],
    )

    axis.set_xlabel("Importance")
    axis.set_ylabel("")
    axis.set_title(title)
    axis.grid(axis="x", alpha=0.3)

    output_file = FIGURES / filename

    figure.tight_layout()
    figure.savefig(
        output_file,
        dpi=FIGURE_DPI,
        bbox_inches="tight",
    )

    plt.close(figure)

    print(f"Saved {output_file}")

    return output_file