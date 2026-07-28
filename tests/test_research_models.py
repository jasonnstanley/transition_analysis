import pytest
from python.research_models import (
    ResearchDashboard,
    ResearchEvidence,
)


def test_research_dashboard_summary() -> None:
    dashboard = ResearchDashboard(
        complete=1,
        total=3,
    )

    assert dashboard.percentage == pytest.approx(33.333333)
    assert dashboard.summary == "1/3 (33.3%)"
    

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
    
    
    
def test_research_evidence_summary() -> None:
    evidence = ResearchEvidence(
        tables=["table_1.tex", "table_2.tex"],
        figures=["figure_1.png"],
        narrative=["interpretation.tex"],
    )

    assert evidence.summary == (
        "4 linked outputs "
        "(2 tables, 1 figure, 1 narrative)"
    )
    
def test_research_evidence_has_evidence() -> None:
    assert not ResearchEvidence().has_evidence

    assert ResearchEvidence(
        tables=["table.tex"]
    ).has_evidence
    
    
def test_research_evidence_empty_summary() -> None:
    evidence = ResearchEvidence()

    assert evidence.summary == (
        "0 linked outputs "
        "(0 tables, 0 figures, 0 narratives)"
    )
    
    
def test_research_dashboard_empty() -> None:
    dashboard = ResearchDashboard(
        complete=0,
        total=0,
    )

    assert dashboard.percentage == 0.0
    assert dashboard.summary == "0/0 (0.0%)"    
    
    
def test_research_dashboard_publication_readiness() -> None:
    assert not ResearchDashboard(
        complete=1,
        total=3,
    ).ready_for_publication

    assert ResearchDashboard(
        complete=3,
        total=3,
    ).ready_for_publication    