from pathlib import Path

EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".idea",
    ".vscode",
    "venv",
    ".venv",
    "env",
    "build",
    "dist",
    "outputs",
    "output",
}

EXCLUDE_FILES = {
    ".DS_Store",
}


def print_tree(path: Path, prefix: str = "") -> None:
    entries = sorted(
        [
            p for p in path.iterdir()
            if p.name not in EXCLUDE_DIRS
            and p.name not in EXCLUDE_FILES
        ],
        key=lambda p: (p.is_file(), p.name.lower())
    )

    for i, entry in enumerate(entries):
        connector = "└── " if i == len(entries) - 1 else "├── "
        print(prefix + connector + entry.name)

        if entry.is_dir():
            extension = "    " if i == len(entries) - 1 else "│   "
            print_tree(entry, prefix + extension)


if __name__ == "__main__":
    print(".")
    print_tree(Path("."))