from pathlib import Path

from python.io import load_data
import python.summary as summary
import python.pivots as pivots


REPORTS = Path("reports")
REPORTS.mkdir(exist_ok=True)

OUTFILE = REPORTS / "summary_report.txt"


def main():
    df = load_data()

    lines = []

    lines.append("Transition Analysis")
    lines.append("------------------------------")
    lines.append(f"Cohort Size : {summary.cohort_size(df)}")
    lines.append(f"Pass Rate   : {summary.pass_rate(df):.2%}")
    lines.append("")

    lines.append("Grade Counts")
    lines.append("------------")
    lines.append(str(summary.grade_counts(df)))
    lines.append("")

    lines.append("SOS Counts")
    lines.append("----------")
    lines.append(str(summary.count_by(df, "SOS Level")))
    lines.append("")

    lines.append("SOS Level vs Current Outcome")
    lines.append("----------------------------")
    lines.append(str(pivots.pivot_counts(df, "SOS Level", "Current Outcome")))
    lines.append("")

    lines.append("Previous 33130 Fail vs Current Outcome")
    lines.append("--------------------------------------")
    lines.append(str(pivots.pivot_counts(df, "Previous 33130 Fail", "Current Outcome")))
    
    lines.append("")
    lines.append("Has 35010 vs Current Outcome")
    lines.append("----------------------------")
    lines.append(str(pivots.pivot_counts(df, "Has 35010", "Current Outcome")))
    lines.append("")
    lines.append("Pass Rate by SOS Level")
    lines.append("----------------------")
    lines.append(str(summary.pass_rate_by(df, "SOS Level")))
    lines.append("")

    lines.append("Pass Rate by Has 35010")
    lines.append("----------------------")
    lines.append(str(summary.pass_rate_by(df, "Has 35010")))
    lines.append("")

    lines.append("Pass Rate by Previous 33130 Fail")
    lines.append("--------------------------------")
    lines.append(str(summary.pass_rate_by(df, "Previous 33130 Fail")))
    
    OUTFILE.write_text("\n".join(lines), encoding="utf-8")

    print(f"Report written to: {OUTFILE}")


if __name__ == "__main__":
    main()