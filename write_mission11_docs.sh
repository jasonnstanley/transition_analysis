#!/usr/bin/env bash
set -euo pipefail

if [ ! -f "README.md" ] || [ ! -d "python" ]; then
    echo "Run this script from the transition_analysis repository root."
    exit 1
fi

mkdir -p docs

cat > README.md <<'EOF'
# Transition Analysis Toolkit

[![Python checks](https://github.com/jasonnstanley/transition_analysis/actions/workflows/python-checks.yml/badge.svg)](https://github.com/jasonnstanley/transition_analysis/actions/workflows/python-checks.yml)

A reproducible research toolkit for analysing student transition pathways into first-year university mathematics. The toolkit integrates statistical modelling, machine-learning comparison, independent R verification, automated reporting, audit logging, and publication-ready outputs.

## Project overview

This repository contains a reproducible analysis workflow for examining relationships between:

- secondary-school mathematics preparation
- prior attempts in preparatory mathematics
- previous attempts in the target subject
- international student status
- composite risk measures
- current subject outcomes

The project combines:

- Python analysis
- independent R verification
- de-identified research data
- schema-based data preparation
- audit logging
- statistical modelling
- machine-learning model comparison
- automated research tables and figures
- automated LaTeX paper generation

## Research context

The current case study analyses Autumn 2026 enrolments in a first-stage undergraduate mathematics subject.

The workflow was designed to support transparent and reproducible investigation of student transition pathways into first-year university mathematics.

## Quick start

Clone the repository and enter the project directory:

```bash
git clone https://github.com/jasonnstanley/transition_analysis.git
cd transition_analysis
```

Create and activate a virtual environment.

### Windows Git Bash

```bash
py -3.14 -m venv .venv
source .venv/Scripts/activate
```

### macOS or Linux

```bash
python3.14 -m venv .venv
source .venv/bin/activate
```

Install the Python dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run the complete reproducible build:

```bash
python -m python.build
```

## Reproducible build

The master build coordinates the canonical research workflow. It performs:

1. environment and project checks
2. Python unit tests
3. canonical Python analysis
4. automated report generation
5. independent R verification
6. LaTeX paper preparation
7. build-status and audit recording

A successful run ends with a `SUCCESS` build status and produces updated research outputs without requiring manual editing of generated tables or figures.

## Repository structure

```text
transition_analysis/
├── python/          Python analysis modules
├── R/               Independent R verification scripts
├── schema/          Research data schema
├── data/
│   ├── processed/   Approved de-identified research datasets
│   └── public/      Public research dataset
├── reports/         Generated tables and model summaries
├── figures/         Generated research figures
├── logs/            Analysis and verification audit logs
├── paper/           Automated LaTeX research paper
├── docs/            Research and developer documentation
├── tests/           Validation and test scripts
└── archive/         Retained legacy scripts and entry points
```

## Outputs

| Location | Contents |
|---|---|
| `reports/` | Statistical summaries, model comparisons, feature rankings, and LaTeX tables |
| `figures/` | Publication-quality research figures |
| `logs/` | Analysis, verification, and build audit records |
| `paper/` | LaTeX manuscript and generated paper components |
| `data/public/` | Approved de-identified public research data |
| `docs/` | Data dictionary, verification report, and project documentation |

Generated outputs should normally be recreated through the canonical build rather than edited manually.

## Verified platforms

The Transition Analysis Toolkit has been successfully built and tested on:

### Windows 11

- Python 3.14.5
- R 4.6.1
- TeX Live 2026

### macOS Monterey 12.7.6 (Intel)

- Python 3.14.6
- R 4.4.1
- TeX Live 2022

The toolkit is designed to provide a reproducible workflow across supported platforms.

## Development workflow

A concise development workflow is documented in [`docs/DeveloperWorkflow.md`](docs/DeveloperWorkflow.md).

Git and shell-history notes are kept separately in [`docs/GitTips.md`](docs/GitTips.md).

## Data and verification

The repository contains approved de-identified research datasets. Data preparation and validation are governed by the research schema in `schema/`.

Independent verification is performed in R using the same approved train/test split used by the canonical Python analysis.

Further details are available in:

- [`docs/research_data_dictionary.md`](docs/research_data_dictionary.md)
- [`docs/verification_report.md`](docs/verification_report.md)

## Citation

Citation metadata is provided in [`CITATION.cff`](CITATION.cff).

Researchers using the toolkit, its workflow, or its published outputs should cite the repository using the citation information supplied by GitHub.

## Licence

This project is released under the terms provided in [`LICENSE`](LICENSE).
EOF

cat > docs/DeveloperWorkflow.md <<'EOF'
# Developer Workflow

This page records the routine development workflow for the Transition Analysis Toolkit.

## Start work

Synchronise the local branch before making changes:

```bash
git pull --rebase origin main
```

Activate the project virtual environment.

### Windows Git Bash

```bash
source .venv/Scripts/activate
```

### macOS or Linux

```bash
source .venv/bin/activate
```

## Develop and test

Run the complete canonical build:

```bash
python -m python.build
```

For a faster local check during development, run:

```bash
python -m pytest
```

The full build should be run before committing changes that affect analysis, reports, verification, or publication outputs.

## Review changes

Inspect the working tree:

```bash
git status --short
```

Review changes before staging:

```bash
git diff
```

Review staged changes:

```bash
git diff --staged
```

## Commit

Stage only the files that belong to the current change:

```bash
git add path/to/file
```

Create a focused commit:

```bash
git commit -m "Describe the completed change"
```

## Synchronise and push

Before pushing, rebase onto the latest remote branch:

```bash
git pull --rebase origin main
```

Push the commit:

```bash
git push origin main
```

Confirm that the repository is clean:

```bash
git status
```

## Recommended sequence

```bash
git pull --rebase origin main
python -m python.build
git status --short
git diff
git add path/to/file
git diff --staged
git commit -m "Describe the completed change"
git pull --rebase origin main
git push origin main
git status
```

## Working across multiple computers

When using the repository on more than one computer:

1. push completed work before changing machines
2. pull with rebase before beginning work
3. avoid making unrelated changes on two machines at the same time
4. resolve any conflict before continuing development
5. confirm a clean working tree after each push
EOF

cat > docs/GitTips.md <<'EOF'
# Git and Shell History Tips

This page records useful commands for locating previous work and understanding the difference between shell history and Git history.

## Search shell command history

To find commands containing `README`:

```bash
history | grep README
```

To find previous staging commands:

```bash
history | grep "git add"
```

To find the command that staged `README.md`:

```bash
history | grep "git add README.md"
```

Shell history answers:

> What commands did I type?

## Interactive shell-history search

In Bash or Git Bash, press:

```text
Ctrl+r
```

Then type part of the command, such as:

```text
README
```

or:

```text
git add
```

Press `Ctrl+r` again to move further back through matching commands. Press Enter to run the selected command, or use the arrow keys to edit it first.

## Inspect Git history for a file

Show commits that changed `README.md`:

```bash
git log -- README.md
```

Use a compact view:

```bash
git log --oneline -- README.md
```

Show the changes introduced by each commit:

```bash
git log -p -- README.md
```

Git history answers:

> When did the tracked file change, and what changed?

## Git workflow model

```text
Working files
      ↓
    git add
      ↓
Staging area
      ↓
  git commit
      ↓
Local Git repository
      ↓
   git push
      ↓
GitHub remote repository
```

## Useful distinction

```text
history | grep ...
```

searches commands entered in the shell.

```text
git log -- path/to/file
```

searches the repository's recorded commit history.

This distinction is especially useful when reconstructing how a file was edited, staged, committed, and published.
EOF

echo
echo "Documentation files written:"
echo "  README.md"
echo "  docs/DeveloperWorkflow.md"
echo "  docs/GitTips.md"
echo
echo "Review with:"
echo "  git diff -- README.md docs/DeveloperWorkflow.md docs/GitTips.md"
