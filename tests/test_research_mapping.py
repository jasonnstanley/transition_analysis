from python.research_mapping import RESEARCH_MAPPING
from python.research_program import RESEARCH_PROGRAM
from python.research_models import ResearchEvidence

def test_research_program_matches_mapping() -> None:
    assert set(RESEARCH_PROGRAM) == set(RESEARCH_MAPPING)
    
def test_research_mapping_uses_research_evidence() -> None:
    for evidence in RESEARCH_MAPPING.values():
        assert isinstance(evidence, ResearchEvidence)
        
        