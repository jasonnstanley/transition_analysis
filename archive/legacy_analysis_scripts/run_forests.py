from python.forests import (
    evaluate_random_forest,
    feature_importance_table,
    fit_random_forest,
    save_feature_importance_plot,
)
from python.io import load_data
from python.ml import split_data


def yn_to_number(series):
    """
    Convert common Yes/No values to 1/0.
    """

    return series.map(
        {
            "Y": 1,
            "N": 0,
            "Yes": 1,
            "No": 0,
        }
    )


def prepare_X(df, features):
    """
    Select and prepare predictor columns.
    """

    X = df[features].copy()

    binary_columns = [
        "Has 35010",
        "Previous 33130 Fail",
        "International Student",
    ]

    for column in binary_columns:
        if column in X.columns:
            X[column] = yn_to_number(X[column])

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

        X_train, X_test, y_train, y_test = split_data(
            X,
            y,
        )

        model = fit_random_forest(
            X_train,
            y_train,
            n_estimators=500,
            random_state=42,
        )

        metrics = evaluate_random_forest(
            model,
            X_test,
            y_test,
        )

        print()
        print("Metrics")
        print("-------")

        for metric, value in metrics.items():
            print(f"{metric}: {value:.3f}")

        importance = feature_importance_table(
            model,
            X.columns,
        )

        print()
        print("Feature Importance")
        print("------------------")
        print(importance)

        file_stem = name.lower().replace(" ", "_")

        importance.to_csv(
            f"outputs/{file_stem}_random_forest_importance.csv",
            index=False,
        )

        save_feature_importance_plot(
            importance,
            filename=f"{file_stem}_random_forest_importance.png",
            title=f"{name} Random Forest Feature Importance",
        )


if __name__ == "__main__":
    main()