from python.tree_data import build_tree_datasets


def print_dataset_summary(dataset) -> None:
    print()
    print(dataset.name)
    print("-" * 72)
    print(f"Rows:       {len(dataset.X):,}")
    print(f"Features:   {len(dataset.X.columns)}")
    print(f"Passes:     {int(dataset.y.sum()):,}")
    print(f"Non-passes: {int((dataset.y == 0).sum()):,}")
    print()
    print("Feature columns:")

    for column in dataset.X.columns:
        print(f"  - {column}")


def main() -> None:
    without_risk, with_risk = build_tree_datasets()

    print("Tree modelling datasets prepared successfully.")

    print_dataset_summary(without_risk)
    print_dataset_summary(with_risk)


if __name__ == "__main__":
    main()