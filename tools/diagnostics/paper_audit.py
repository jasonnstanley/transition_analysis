from pathlib import Path
from pypdf import PdfReader
import re

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PDF_FILE = PROJECT_ROOT / "paper" / "build" / "main.pdf"


def main():
    print("=" * 60)
    print("Paper Audit")
    print("=" * 60)

    if not PDF_FILE.exists():
        raise FileNotFoundError(PDF_FILE)

    reader = PdfReader(PDF_FILE)

    print(f"PDF found : {PDF_FILE}")
    print(f"Pages     : {len(reader.pages)}")
    
    text = ""

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted

#    print("\nFirst 2,000 extracted characters")
#    print("--------------------------------")
#    print(text[:2000])

    print(f"Characters: {len(text):,}")
    print(f"Words     : {len(text.split()):,}")
    required_sections = [
        "Abstract",
        "Introduction",
        "Methodology",
        "Results",
        "Discussion",
        "Conclusion",
        "References",
    ]

    print("\nRequired sections")

    for section in required_sections:
        status = "PASS" if section in text else "FAIL"
        print(f"{section:<15}: {status}")

    abstract_match = re.search(
        r"Abstract\s+(.*?)(?=\s+Keywords:|\s+\d+\s+Introduction)",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    print("\nAbstract")

    abstract_ok = False

    if abstract_match:
        abstract_text = abstract_match.group(1)
        abstract_words = len(abstract_text.split())
        abstract_ok = 180 <= abstract_words <= 200

        print(f"Words          : {abstract_words}")
        print(f"Journal target : {'PASS' if abstract_ok else 'FAIL'}")
    else:
        print("Abstract text  : FAIL")
    
    unresolved_markers = ["??", "[?]"]

    print("\nUnresolved references")

    found_unresolved = False

    for marker in unresolved_markers:
        if marker in text:
            print(f"{marker:<15}: FAIL")
            found_unresolved = True

    if not found_unresolved:
        print("None found     : PASS")    
        
    print("\nStatus")
    print("------")

    passed = (
        all(section in text for section in required_sections)
        and not found_unresolved
        and abstract_ok
    )

    print("PASS" if passed else "FAIL")    
        
        

if __name__ == "__main__":
    main()