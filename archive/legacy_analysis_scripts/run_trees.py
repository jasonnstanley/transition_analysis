from python.io import load_data
from python.ml import split_data
from python.trees import (
    fit_decision_tree,
    evaluate_decision_tree,
    print_tree_rules,
    feature_importance_table,
    save_tree_plot,
    save_feature_importance_plot,
)


def yn_to_number(series):
    return series.map({
        "Y": 1,
        "N": 0,
        "Yes": 1,
        "No": 0,
    })


def prepare_X(df, features):
    X = df[features].copy()

    binary_columns = [
        "Has 35010",
        "Previous 33130 Fail",
        "International Student",
    ]

    for col in binary_columns:
        if col in X.columns:
            X[col] = yn_to_number(X[col])

    return X


def main():
    df = load_data()
    y = df["Pass 33130"]

    feature_sets = {
        "With Risk Index": [
            "Risk Index",
            "Has 35010",
            "Previous 33130 Fail",
            "International Student",
        ],
        "Without Risk Index": [
            "Has 35010",
            "Previous 33130 Fail",
            "International Student",
        ],
    }

    for name, features in feature_sets.items():
        print()
        print("=" * 60)
        print(name)
        print("=" * 60)

        X = prepare_X(df, features)
        X_train, X_test, y_train, y_test = split_data(X, y)
        
        model = fit_decision_tree(
            X_train,
            y_train,
            max_depth=3,
        )

        metrics = evaluate_decision_tree(
            model,
            X_test,
            y_test,
         )

        print()
        print("Metrics")
        print("-------")
        for key, value in metrics.items():
            print(f"{key}: {value:.3f}")

        print()
        print("Tree Rules")
        print("----------")
        print_tree_rules(model, X.columns)
        print()
        print("Feature Importance")
        print("------------------")

        importance = feature_importance_table(
            model,
            X.columns,
        )

        print(importance)

        save_tree_plot(
            model,
            X.columns,
            filename=f"{name.lower().replace(' ', '_')}_tree.png",
            title=name,
        )

        save_feature_importance_plot(
            importance,
            filename=f"{name.lower().replace(' ', '_')}_importance.png",
            title=f"{name} Feature Importance",
        )

if __name__ == "__main__":
    main()