"""
Generate evidence summaries for each research question.
"""
from pathlib import Path
from python.research_mapping import RESEARCH_MAPPING
from python.research_program import RESEARCH_PROGRAM

OUTPUT_FILE = Path("reports") / "research_evidence.md"

program_keys = set(RESEARCH_PROGRAM)
mapping_keys = set(RESEARCH_MAPPING)

if program_keys != mapping_keys:
    missing_from_mapping = sorted(program_keys - mapping_keys)
    missing_from_program = sorted(mapping_keys - program_keys)

    raise RuntimeError(
        "Research programme and evidence mapping do not match. "
        f"Missing from mapping: {missing_from_mapping}; "
        f"missing from programme: {missing_from_program}"
    )

def main() -> None:
    lines = [
        "# Research Evidence Summary",
        "",
    ]
    
    print("=" * 72)
    print("Research Evidence Summary")
    print("=" * 72)

    for rq, details in RESEARCH_MAPPING.items():
        question = RESEARCH_PROGRAM[rq]
        
        evidence_count = (
            details.count
        )

        
        
        lines.append(f"## {rq}")
        lines.append(f"**Status:** {details.status}")
        lines.append("")
        lines.append("")
        lines.append(question)
        lines.append("")

        lines.append("### Tables")
        for table in details.tables:
            lines.append(f"- `{table}`")

        lines.append("")
        lines.append("### Figures")
        for figure in details.figures:
            lines.append(f"- `{figure}`")

        lines.append("")
        lines.append("### Narrative")
        for item in details.narrative:
            lines.append(f"- `{item}`")

        lines.append("")
        
        print()
        print(
            f"{rq} [{details.status}]: "
            f"{question}"
        )

        print("  Tables")
        for table in details.tables:
            print(f"    - {table}")

        print("  Figures")
        for figure in details.figures:
            print(f"    - {figure}")

        print("  Narrative")
        for item in details.narrative:
            print(f"    - {item}")

    OUTPUT_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

print()
print(f"Evidence report written: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()