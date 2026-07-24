from pathlib import Path


REPORT_PATH = Path("reports/model_interpretation.md")
LATEX_REPORT_PATH = Path("reports/model_interpretation.tex")

def test_model_interpretation_report_exists():
    assert REPORT_PATH.exists()


def test_model_interpretation_report_has_expected_sections():
    content = REPORT_PATH.read_text(encoding="utf-8")

    assert "# Model Interpretation" in content
    assert "## Cross-model interpretation" in content
    assert "Across the tuned tree-based models" in content
    assert "mean importance =" in content
    assert "Together, these three groups accounted for" in content
    assert "%" in content
    assert "This suggests that prior secondary mathematics preparation" in content
    assert "appeared in" in content
    assert "Secondary mathematics preparation remained influential across all" in content
    
def test_model_interpretation_latex_report_exists():
    assert LATEX_REPORT_PATH.exists()


def test_model_interpretation_latex_report_contains_narrative_only():
    content = LATEX_REPORT_PATH.read_text(encoding="utf-8")

    assert "Across the tuned tree-based models" in content
    assert r"\section{Model Interpretation}" not in content