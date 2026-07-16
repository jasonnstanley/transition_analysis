from python.research_io import load_research_data
from python.schema import load_research_schema
from python.splash import splash


def main() -> None:
    schema = load_research_schema()
    dataframe = load_research_data()

    identifier_column = schema[
        "identifiers"
    ][
        "research_identifier"
    ][
        "column"
    ]

    splash(
        schema=schema,
        dataframe=dataframe,
        identifier_column=identifier_column,
    )

    print()
    print("Research dataset validation passed.")
    print(f"Rows:    {len(dataframe):,}")
    print(f"Columns: {len(dataframe.columns)}")
    print()
    print("Research columns:")

    for column in dataframe.columns:
        print(f"  - {column}")


if __name__ == "__main__":
    main()