"""Environment and project checks for the Transition Analysis Toolkit."""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DIRECTORIES = [
    "data",
    "data/processed",
    "figures",
    "logs",
    "reports",
    "schema",
    "tests",
]

REQUIRED_FILES = [
    "data/processed/transition_research.csv",
    "data/processed/train_test_split.csv",
    "schema/research_schema.yaml",
]

REQUIRED_PACKAGES = [
    "numpy",
    "pandas",
    "sklearn",
    "matplotlib",
    "yaml",
]

EXTERNAL_COMMANDS = {
    "Git": ["git", "--version"],
    "R": ["Rscript", "--version"],
    "pdfLaTeX": ["pdflatex", "--version"],
    "latexmk": ["latexmk", "--version"],
    "BibTeX": ["bibtex", "--version"],
}


def print_heading(title: str) -> None:
    """Print a section heading."""
    print()
    print(title)
    print("-" * 72)


def check_python() -> bool:
    """Check the Python version and virtual environment."""
    print_heading("Python environment")

    print(f"Python executable : {sys.executable}")
    print(f"Python version    : {sys.version.split()[0]}")

    in_virtual_environment = (
        sys.prefix != getattr(sys, "base_prefix", sys.prefix)
        or "VIRTUAL_ENV" in os.environ
    )

    if in_virtual_environment:
        print("Virtual environment: ACTIVE")
        return True

    print("Virtual environment: NOT ACTIVE")
    return False


def check_packages() -> bool:
    """Check required Python packages."""
    print_heading("Python packages")

    all_available = True

    for package in REQUIRED_PACKAGES:
        available = importlib.util.find_spec(package) is not None
        status = "FOUND" if available else "MISSING"
        print(f"{package:<20} {status}")
        all_available &= available

    return all_available


def check_directories() -> bool:
    """Check required project directories."""
    print_heading("Project directories")

    all_available = True

    for relative_path in REQUIRED_DIRECTORIES:
        path = PROJECT_ROOT / relative_path
        exists = path.is_dir()
        status = "FOUND" if exists else "MISSING"
        print(f"{relative_path:<35} {status}")
        all_available &= exists

    return all_available


def check_files() -> bool:
    """Check required project files."""
    print_heading("Required project files")

    all_available = True

    for relative_path in REQUIRED_FILES:
        path = PROJECT_ROOT / relative_path
        exists = path.is_file()
        status = "FOUND" if exists else "MISSING"
        print(f"{relative_path:<50} {status}")
        all_available &= exists

    return all_available


def find_texlive_command(command: str) -> str | None:
    """Find a TeX command either on PATH or in the local Tools installation."""
    path_command = shutil.which(command)

    if path_command:
        return path_command

    local_command = (
        PROJECT_ROOT.parent.parent
        / "Tools"
        / "texlive"
        / "2026"
        / "bin"
        / "windows"
        / f"{command}.exe"
    )

    if local_command.is_file():
        return str(local_command)

    return None


def find_rscript_command() -> str | None:
    """Find Rscript either on PATH or in the local Tools installation."""
    path_command = shutil.which("Rscript")

    if path_command:
        return path_command

    local_command = (
        PROJECT_ROOT.parent.parent
        / "Tools"
        / "R"
        / "bin"
        / "Rscript.exe"
    )

    if local_command.is_file():
        return str(local_command)

    return None


def resolve_command(command: list[str]) -> list[str] | None:
    """Resolve an external command to an executable path."""
    executable = command[0]

    if executable in {"pdflatex", "latexmk", "bibtex"}:
        resolved = find_texlive_command(executable)
    elif executable == "Rscript":
        resolved = find_rscript_command()
    else:
        resolved = shutil.which(executable)

    if resolved is None:
        return None

    return [resolved, *command[1:]]


def check_external_commands() -> bool:
    """Check Git, R, and LaTeX command availability."""
    print_heading("External tools")

    all_available = True

    for name, command in EXTERNAL_COMMANDS.items():
        resolved_command = resolve_command(command)

        if resolved_command is None:
            print(f"{name:<20} MISSING")
            all_available = False
            continue

        try:
            result = subprocess.run(
                resolved_command,
                capture_output=True,
                text=True,
                check=False,
                timeout=20,
            )

            output = result.stdout.strip() or result.stderr.strip()
            first_line = output.splitlines()[0] if output else "available"

            if result.returncode == 0:
                print(f"{name:<20} FOUND — {first_line}")
            else:
                print(f"{name:<20} ERROR — exit code {result.returncode}")
                all_available = False

        except (OSError, subprocess.SubprocessError) as error:
            print(f"{name:<20} ERROR — {error}")
            all_available = False

    return all_available


def check_git_repository() -> bool:
    """Check whether the project root is inside a Git repository."""
    print_heading("Git repository")

    git = shutil.which("git")

    if git is None:
        print("Git repository check: SKIPPED — Git not available")
        return False

    result = subprocess.run(
        [git, "rev-parse", "--show-toplevel"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode == 0:
        repository_root = Path(result.stdout.strip()).resolve()
        print(f"Repository root: {repository_root}")
        return repository_root == PROJECT_ROOT.resolve()

    print("Git repository: NOT DETECTED")
    return False


def main() -> int:
    """Run all environment and project checks."""
    print("=" * 72)
    print("Transition Analysis Toolkit — Environment Check")
    print("=" * 72)
    print(f"Project root: {PROJECT_ROOT}")

    checks = {
        "Python environment": check_python(),
        "Python packages": check_packages(),
        "Project directories": check_directories(),
        "Required files": check_files(),
        "External tools": check_external_commands(),
        "Git repository": check_git_repository(),
    }

    print_heading("Summary")

    for name, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        print(f"{name:<30} {status}")

    required_checks = [
        checks["Python environment"],
        checks["Python packages"],
        checks["Project directories"],
        checks["Required files"],
        checks["External tools"],
    ]

    if all(required_checks):
        print()
        print("Environment check completed successfully.")
        return 0

    print()
    print("Environment check failed. Review the missing requirements above.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())