from python.research_mapping import RESEARCH_MAPPING
from python.research_program import RESEARCH_PROGRAM
from python.research_models import ResearchDashboard


def build_dashboard() -> ResearchDashboard:
    return ResearchDashboard(
        complete=supported_question_count(),
        total=total_question_count(),
    )
    
    
def supported_question_count() -> int:
    return sum(
        evidence.has_evidence
        for evidence in RESEARCH_MAPPING.values()
    )
    
def total_question_count() -> int:
    return len(RESEARCH_MAPPING)    
    

def main() -> None:
    print("=" * 72)
    print("Research Dashboard")
    print("=" * 72)

    

    for rq, evidence in RESEARCH_MAPPING.items():
        question = RESEARCH_PROGRAM[rq]

        print(f"{rq}: {evidence.status}")
        print(f"  {question}")
        print(f"  {evidence.summary}")
        print()

        

    print("-" * 72)
    
    dashboard = build_dashboard()

    print(
        f"Progress: {dashboard.summary} "
        "research questions supported"
    )
    
    readiness = (
        "READY"
        if dashboard.ready_for_publication
        else "NOT READY"
    )

    print(f"Publication readiness: {readiness}")




if __name__ == "__main__":
    main()