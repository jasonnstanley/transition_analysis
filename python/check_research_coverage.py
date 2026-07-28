"""
Verify that every research question has supporting evidence.
"""
import argparse
from python.research_mapping import RESEARCH_MAPPING
from python.research_program import RESEARCH_PROGRAM


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
    parser = argparse.ArgumentParser(
        description="Check research-question evidence coverage."
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail when research questions have no linked evidence.",
    )
    args = parser.parse_args()

    print("=" * 72)
    print("Research Coverage Check")
    print("=" * 72)
    pending_questions = []
    
    for rq, details in RESEARCH_MAPPING.items():
        
        evidence = details.count
                
        question = RESEARCH_PROGRAM[rq]
        
        status = "PASS" if details.has_evidence else "PENDING"

        if not details.has_evidence:
            pending_questions.append(rq)
            
        print(
            f"{rq}: {details.status} "
            f"{details.summary}"
        )
        print(f"  {question}")
        
    if pending_questions and args.strict:
        raise RuntimeError(
            "Research questions without linked evidence: "
            + ", ".join(pending_questions)
        )
    if pending_questions:
        print()
        print(
            "Coverage incomplete: "
            + ", ".join(pending_questions)
            + " require linked evidence."
        )
    else:
        print()
        print("Coverage complete: all research questions have linked evidence.")
    
if __name__ == "__main__":
    main()