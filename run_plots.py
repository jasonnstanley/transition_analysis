from python.io import load_data
import python.summary as summary
import python.plots as plots


def main():

    df = load_data()

    sos = summary.distribution_by(df, "SOS Level")

    plots.bar_chart(
        sos,
        "Distribution of SOS Levels",
        " ",
        "fig01_sos_distribution.png"
    )

    grades = summary.grade_distribution(df)
    
    plots.bar_chart(
        grades,
        "Current Outcome Distribution",
        " ",
        "fig02_grade_distribution.png"
    )


    passrate = summary.pass_rate_by(df, "SOS Level")
    
    plots.bar_chart(
        passrate["PassRate"],
        "Pass Rate by SOS Level",
        "Pass Rate (%)",
        "fig03_pass_rate_by_sos.png"
    )

    pathway = summary.pass_rate_by(df, "Has 35010")

    plots.bar_chart(
        pathway["PassRate"],
        "Pass Rate by 35010 Pathway",
        "Pass Rate (%)",
        "fig03_pass_rate_35010.png"
    )
    
    previous_fail = summary.pass_rate_by(df, "Previous 33130 Fail")

    plots.bar_chart(
        previous_fail["PassRate"],
        "Pass Rate by Previous 33130 Failure",
        "Pass Rate (%)",
        "fig04_pass_rate_previous33130fail.png"
    )
    
    risk = summary.pass_rate_by(df, "Risk Index")

    plots.bar_chart(
        risk["PassRate"],
        "Pass Rate by Transition Risk Score",
        "Pass Rate (%)",
        "fig05_pass_rate_risk_index.png"
    )
    
    
    
if __name__ == "__main__":
    main()