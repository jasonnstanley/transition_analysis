"""Discover external command-line tools used by the toolkit."""

from __future__ import annotations

import os
import shutil
from pathlib import Path


class ToolNotFoundError(RuntimeError):
    """Raised when a required external tool cannot be located."""


def _first_existing_file(candidates: list[Path]) -> Path | None:
    """Return the first candidate that exists and is a file."""

    for candidate in candidates:
        candidate = candidate.expanduser().resolve()

        if candidate.is_file():
            return candidate

    return None


def find_executable(
    executable_name: str,
    *,
    candidates: list[Path] | None = None,
) -> Path:
    """
    Locate an executable using PATH and optional fallback locations.

    Search order:
    1. System or user PATH.
    2. Explicit candidate locations.
    """

    path_result = shutil.which(executable_name)

    if path_result:
        return Path(path_result).resolve()

    candidate_result = _first_existing_file(candidates or [])

    if candidate_result:
        return candidate_result

    searched_locations = "\n".join(
        f"  - {candidate.expanduser()}"
        for candidate in candidates or []
    )

    message = (
        f"Required tool '{executable_name}' was not found on PATH."
    )

    if searched_locations:
        message += (
            "\nThe following fallback locations were also checked:\n"
            f"{searched_locations}"
        )

    raise ToolNotFoundError(message)


def find_rscript() -> Path:
    """Locate the Rscript executable."""

    home = Path.home()

    candidates = [
        home / "Tools" / "R" / "bin" / "Rscript.exe",
        home / "Tools" / "R" / "bin" / "x64" / "Rscript.exe",
    ]

    return find_executable(
        "Rscript",
        candidates=candidates,
    )


def find_git() -> Path:
    """Locate the Git executable."""

    home = Path.home()

    candidates = [
        home / "Tools" / "Git" / "bin" / "git.exe",
        home / "Tools" / "Git" / "cmd" / "git.exe",
        home / "Tools" / "PortableGit" / "bin" / "git.exe",
        home / "Tools" / "PortableGit" / "cmd" / "git.exe",
    ]

    return find_executable(
        "git",
        candidates=candidates,
    )


def find_pdflatex() -> Path:
    """Locate the pdfLaTeX executable."""

    home = Path.home()
    texlive_root = home / "Tools" / "texlive"

    candidates = [
        texlive_root / "bin" / "windows" / "pdflatex.exe",
        home / "Tools" / "TeXLive" / "bin" / "windows" / "pdflatex.exe",
    ]

    if texlive_root.is_dir():
        candidates.extend(
            sorted(
                texlive_root.glob("*/bin/windows/pdflatex.exe"),
                reverse=True,
            )
        )

    return find_executable(
        "pdflatex",
        candidates=candidates,
    )


def find_pandoc() -> Path:
    """Locate the Pandoc executable."""

    home = Path.home()

    candidates = [
        home / "Tools" / "Pandoc" / "pandoc.exe",
        home / "AppData" / "Local" / "Pandoc" / "pandoc.exe",
    ]

    return find_executable(
        "pandoc",
        candidates=candidates,
    )


def describe_tool(name: str, path: Path) -> str:
    """Return a readable tool-location description."""

    return f"{name}: {path}"


def main() -> None:
    """Display the external tools currently available."""

    tool_finders = [
        ("Rscript", find_rscript),
        ("Git", find_git),
        ("pdfLaTeX", find_pdflatex),
        ("Pandoc", find_pandoc),
    ]

    print("External tool discovery")
    print("=" * 72)

    for name, finder in tool_finders:
        try:
            path = finder()
        except ToolNotFoundError as exc:
            print(f"{name}: NOT FOUND")
            print(f"  {exc}")
        else:
            print(describe_tool(name, path))


if __name__ == "__main__":
    main()