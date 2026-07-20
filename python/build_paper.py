"""Build the Transition Analysis Toolkit research paper."""

from __future__ import annotations

import subprocess
from pathlib import Path

from python.tools import find_pdflatex
from python.tools import find_bibtex, find_pdflatex


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = PROJECT_ROOT / "paper"
BUILD_DIR = PAPER_DIR / "build"
MAIN_TEX = PAPER_DIR / "main.tex"
OUTPUT_PDF = BUILD_DIR / "main.pdf"
AUX_FILE = BUILD_DIR / "main.aux"

REQUIRED_INPUTS = [
    PROJECT_ROOT / "reports" / "tuned_roc_summary.tex",
    PROJECT_ROOT / "reports" / "grouped_feature_importance.tex",
    PROJECT_ROOT / "reports" / "feature_rankings.tex",
    PROJECT_ROOT / "paper" / "chapters" / "introduction.tex",
    PROJECT_ROOT / "paper" / "chapters" / "methodology.tex",
    PROJECT_ROOT / "paper" / "chapters" / "results.tex",
    PROJECT_ROOT / "paper" / "chapters" / "discussion.tex",
    PROJECT_ROOT / "paper" / "chapters" / "conclusion.tex",
    PROJECT_ROOT / "paper" / "appendix" / "appendix.tex",
    PROJECT_ROOT / "paper" / "bib" / "references.bib",
]


def check_inputs() -> None:
    """Verify that the paper and generated report inputs exist."""

    required_files = [
        MAIN_TEX,
        *REQUIRED_INPUTS,
    ]

    missing_files = [
        path
        for path in required_files
        if not path.is_file()
    ]

    if missing_files:
        missing_text = "\n".join(
            f"  - {path}"
            for path in missing_files
        )

        raise FileNotFoundError(
            "Required paper inputs are missing:\n"
            f"{missing_text}"
        )


def run_pdflatex(pass_number: int) -> None:
    """Run one pdfLaTeX compilation pass."""

    pdflatex = find_pdflatex()

    command = [
        str(pdflatex),
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-output-directory=build",
        "main.tex",
    ]

    print()
    print("-" * 72)
    print(f"pdfLaTeX pass {pass_number}")
    print("-" * 72)
    print(f"Command: {' '.join(command)}")
    print()

    result = subprocess.run(
        command,
        cwd=PAPER_DIR,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Paper build failed during "
            f"pdfLaTeX pass {pass_number} "
            f"with exit code {result.returncode}"
        )

    print()
    print(f"✓ pdfLaTeX pass {pass_number}")

def run_bibtex() -> bool:
    """Run BibTeX when the paper contains citation commands."""

    if not AUX_FILE.is_file():
        raise FileNotFoundError(
            f"Expected LaTeX auxiliary file was not created: {AUX_FILE}"
        )

    aux_text = AUX_FILE.read_text(
        encoding="utf-8",
        errors="replace",
    )

    if "\\citation" not in aux_text:
        print()
        print("-" * 72)
        print("BibTeX")
        print("-" * 72)
        print("No citation commands found — BibTeX skipped.")
        return False

    bibtex = find_bibtex()

    command = [
        str(bibtex),
        "build/main",
    ]

    print()
    print("-" * 72)
    print("BibTeX")
    print("-" * 72)
    print(f"Command: {' '.join(command)}")
    print()

    result = subprocess.run(
        command,
        cwd=PAPER_DIR,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Paper bibliography build failed "
            f"with exit code {result.returncode}"
        )

    print()
    print("✓ BibTeX")
    return True
    
    
def main() -> None:
    """Build the research paper."""

    print("=" * 72)
    print("Transition Analysis Toolkit — Paper Build")
    print("=" * 72)
    print(f"Paper source : {MAIN_TEX}")
    print(f"Build folder : {BUILD_DIR}")

    check_inputs()

    BUILD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    run_pdflatex(pass_number=1)

    bibliography_built = run_bibtex()

    run_pdflatex(pass_number=2)

    if bibliography_built:
        run_pdflatex(pass_number=3)

    if not OUTPUT_PDF.is_file():
        raise FileNotFoundError(
            f"Expected paper PDF was not created: {OUTPUT_PDF}"
        )

    print()
    print("=" * 72)
    print("PAPER BUILD COMPLETED SUCCESSFULLY")
    print("=" * 72)
    print(f"PDF: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()