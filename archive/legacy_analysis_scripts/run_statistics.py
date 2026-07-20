from python.io import load_data
import python.statistics as stats


def main():

    df = load_data()

    result = stats.chi_square(
        df,
        "SOS Level",
        "Pass 33130"
    )

    print()

    print("Chi-square Test")

    print("----------------")

    print(f"Chi-square : {result['chi2']:.3f}")

    print(f"df         : {result['dof']}")

    print(f"p-value    : {result['p']:.6f}")
    
    
    v = stats.cramers_v(
        df,
        "SOS Level",
        "Pass 33130"
    )

    print(f"Cramer's V : {v:.3f}")
    
    


if __name__ == "__main__":
    main()