import pandas as pd

from python.schema import (
    load_research_schema,
    release_output_file,
)
from python.splash import splash


def main() -> None:
    schema = load_research_schema()

    research_path = release_output_file(
        schema,
        "research",
    )

    dataframe = pd.read_csv(research_path)

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


if __name__ == "__main__":
    main()