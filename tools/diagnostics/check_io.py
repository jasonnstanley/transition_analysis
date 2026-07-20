from python.io import load_data
import python.summary as summary

df = load_data()

print("\nTransition Analysis")
print("------------------------------")

print(f"Cohort Size : {summary.cohort_size(df)}")
print(f"Pass Rate   : {summary.pass_rate(df):.2%}")

print("\nGrade Counts")
print("------------")
print(summary.grade_counts(df))

print("\nGrade Distribution")
print("------------------")
print(summary.grade_distribution(df))

print("\nSOS Counts")
print("----------")
print(summary.count_by(df, "SOS Level"))

print("\nSOS Distribution")
print("----------------")
print(summary.distribution_by(df, "SOS Level"))