from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).resolve().parents[3]

PAPER_DIR = PROJECT_ROOT / "paper"
BIB_FILE = PAPER_DIR / "bib" / "references.bib"

def extract_bib_keys(bib_path: Path):
    text = bib_path.read_text(encoding="utf-8")

    keys = []
    for match in re.finditer(r"@\w+\s*\{\s*([^,]+)\s*,", text):
        keys.append(match.group(1).strip())

    return keys

def extract_citation_keys(paper_dir: Path):
    citation_keys = set()

    for tex_path in paper_dir.rglob("*.tex"):
        text = tex_path.read_text(encoding="utf-8")

        for match in re.finditer(r"\\cite\w*\{([^}]+)\}", text):
            for key in match.group(1).split(","):
                citation_keys.add(key.strip())

    return citation_keys

    
def main():
    print("=" * 60)
    print("Bibliography Audit")
    print("=" * 60)

    bib_keys = extract_bib_keys(BIB_FILE)
    citation_keys = extract_citation_keys(PAPER_DIR)

    print(f"Bib entries     : {len(bib_keys)}")
    print(f"Cited entries   : {len(citation_keys)}")

    bib_key_set = set(bib_keys)

    missing_keys = sorted(citation_keys - bib_key_set)
    unused_keys = sorted(bib_key_set - citation_keys)

    print(f"Missing entries : {len(missing_keys)}")
    print(f"Unused entries  : {len(unused_keys)}")

    if missing_keys:
        print("\nMissing bibliography entries")
        for key in missing_keys:
            print(f"  {key}")

    if unused_keys:
        print("\nUnused bibliography entries")
        for key in unused_keys:
            print(f"  {key}")
            
    if unused_keys:
        print("\nUnused bibliography entries")
        print("  Master bibliography entries not cited in this paper.")
        print("  This is informational only.")        
        
    if missing_keys:
        print("\nStatus: FAIL")
    else:
        print("\nStatus: PASS")    
    
if __name__ == "__main__":
    main()