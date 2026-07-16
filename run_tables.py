from pathlib import Path

from python.io import load_data
import python.summary as summary
import python.pivots as pivots


OUTPUTS = Path("outputs")
OUTPUTS.mkdir(exist_ok=True)


def save_table(table, filename):
    path = OUTPUTS / filename
    table.to_csv(path)
    print(f"Saved: {path}")


def main():
    df = load_data()

    save_table(
        summary.pass_rate_by(df, "SOS Level"),
        "pass_rate_by_sos_level.csv"
    )

    save_table(
        summary.pass_rate_by(df, "Has 35010"),
        "pass_rate_by_has35010.csv"
    )

    save_table(
        summary.pass_rate_by(df, "Previous 33130 Fail"),
        "pass_rate_by_previous33130fail.csv"
    )

    save_table(
        pivots.pivot_counts(df, "SOS Level", "Current Outcome"),
        "pivot_sos_level_current_outcome_counts.csv"
    )

    save_table(
        pivots.pivot_percent(df, "SOS Level", "Current Outcome"),
        "pivot_sos_level_current_outcome_percent.csv"
    )


if __name__ == "__main__":
    main()