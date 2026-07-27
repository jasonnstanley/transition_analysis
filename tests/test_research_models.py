from python.research_models import ResearchEvidence


def test_research_evidence_count() -> None:
    evidence = ResearchEvidence(
        tables=["table_1.tex", "table_2.tex"],
        figures=["figure_1.png"],
        narrative=["interpretation.tex"],
    )

    assert evidence.count == 4
    
def test_research_evidence_status_complete() -> None:
    evidence = ResearchEvidence(
        tables=["table_1.tex"],
    )

    assert evidence.status == "Complete"


def test_research_evidence_status_in_progress() -> None:
    evidence = ResearchEvidence()

    assert evidence.status == "In Progress"    
    