from python.io import load_data
import python.summary as summary
import python.pivots as pivots

def main():
    df = load_data()

    print()
    print("Transition Analysis")
    print("------------------------------")

    print(f"Cohort Size : {summary.cohort_size(df)}")
    print(f"Pass Rate   : {summary.pass_rate(df):.2%}")

    print()
    print("Grade Counts")
    print("------------")
    print(summary.grade_counts(df))

    print()
    print("Grade Distribution")
    print("------------------")
    print(summary.grade_distribution(df))

    print()
    print("SOS Counts")
    print("----------")
    print(summary.count_by(df, "SOS Level"))

    print()
    print("SOS Distribution")
    print("----------------")
    print(summary.distribution_by(df, "SOS Level"))
    print()
    print("SOS Level vs Current Outcome")
    print("----------------------------")

    print(
        pivots.pivot_counts(
            df,
            "SOS Level",
            "Current Outcome"
        )
    )
    print(
        pivots.pivot_percent(
            df,
            "SOS Level",
            "Current Outcome"
        )
    )
    print(
        pivots.pivot_counts(
            df,
            "Previous 33130 Fail",
            "Current Outcome"
        )    
    )
    print(
        pivots.pivot_counts(
            df,
            "Has 35010",
            "Current Outcome"
        )
    )
if __name__ == "__main__":
    main()