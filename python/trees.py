"""
Decision tree models and visualisations
for the Transition Analysis Toolkit.
"""

import matplotlib.pyplot as plt
import pandas as pd

from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.tree import (
    DecisionTreeClassifier,
    export_text,
    plot_tree,
)

from python.config import (
    FIGURE_DPI,
    FIGURE_SIZE,
    FIGURES,
    RANDOM_STATE,
    TREE_FIGURE_SIZE,
    TREE_MAX_DEPTH,
)


def fit_decision_tree(
    X_train,
    y_train,
    max_depth=TREE_MAX_DEPTH,
    random_state=RANDOM_STATE,
):
    """
    Fit a balanced Decision Tree classifier.
    """

    model = DecisionTreeClassifier(
        max_depth=max_depth,
        random_state=random_state,
        class_weight="balanced",
    )

    model.fit(X_train, y_train)

    return model


def evaluate_decision_tree(model, X_test, y_test):
    """
    Evaluate a fitted Decision Tree on test data.
    """

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    return {
        "Accuracy": accuracy_score(y_test, predictions),
        "ROC AUC": roc_auc_score(y_test, probabilities),
    }


def print_tree_rules(model, feature_names):
    """
    Print readable Decision Tree rules.
    """

    rules = export_text(
        model,
        feature_names=list(feature_names),
    )

    print(rules)


def feature_importance_table(model, feature_names):
    """
    Return a table of Decision Tree feature importances.
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


def save_tree_plot(
    model,
    feature_names,
    filename,
    title="Decision Tree",
):
    """
    Save a graphical representation of a Decision Tree.
    """

    figure, axis = plt.subplots(figsize=TREE_FIGURE_SIZE)

    plot_tree(
        model,
        feature_names=list(feature_names),
        class_names=["Fail", "Pass"],
        filled=True,
        rounded=True,
        impurity=True,
        proportion=False,
        precision=3,
        ax=axis,
    )

    axis.set_title(title)

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


def save_feature_importance_plot(
    importance_table,
    filename,
    title="Decision Tree Feature Importance",
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