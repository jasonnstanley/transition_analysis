from python.schema import (
    load_research_schema,
    release_output_file,
    schema_version,
    source_file,
)


def main() -> None:
    schema = load_research_schema()

    print("Research schema loaded successfully.")
    print(f"Name:     {schema['schema']['name']}")
    print(f"Version:  {schema_version(schema)}")
    print(f"Source:   {source_file(schema)}")
    print(
        "Research:",
        release_output_file(schema, "research"),
    )
    print(
        "Public:  ",
        release_output_file(schema, "public"),
    )
    print(f"Columns:  {len(schema['columns'])}")


if __name__ == "__main__":
    main()