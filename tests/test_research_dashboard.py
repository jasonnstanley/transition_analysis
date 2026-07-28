import pytest
from python.research_models import (
    ResearchDashboard,
    ResearchEvidence,
)
from python.research_mapping import RESEARCH_MAPPING

from python.research_dashboard import build_dashboard


def test_build_dashboard() -> None:
    dashboard = build_dashboard()

    assert dashboard.complete == 2
    assert dashboard.total == 3
    assert dashboard.summary == "2/3 (66.7%)"
    assert not dashboard.ready_for_publication
    
    
