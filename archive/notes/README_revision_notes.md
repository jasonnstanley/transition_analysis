# README improvements (recommended)

## Opening

```markdown
# Transition Analysis Toolkit

[![Python checks](https://github.com/jasonnstanley/transition_analysis/actions/workflows/python-checks.yml/badge.svg)](https://github.com/jasonnstanley/transition_analysis/actions/workflows/python-checks.yml)

A reproducible research toolkit for analysing student transition pathways into first-year university mathematics. The toolkit integrates statistical modelling, machine-learning comparison, independent R verification, automated reporting, audit logging, and publication-ready outputs.

The repository accompanies a research case study while providing a reusable, transparent workflow for reproducible educational data analysis.
```

---

## Quick Start

### Windows

```bash
py -m venv .venv
source .venv/Scripts/activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

> Independent verification requires a working installation of R. When available, the canonical build automatically runs the independent R verification scripts.

Run the complete build:

```bash
python -m python.build
```

---

## Reproducible build

The master build coordinates the canonical research workflow by performing:

1. Environment and project checks
2. Python unit tests
3. Canonical Python analysis
4. Automated report generation
5. Independent R verification
6. LaTeX paper preparation
7. Build-status and audit recording

A successful run concludes with a `SUCCESS` build status and regenerates all research outputs from source data without requiring manual editing of generated reports, tables, or figures.

---

## Repository structure

```text
transition_analysis/
├── archive/         Retained legacy scripts and entry points
├── data/
│   ├── processed/   Approved de-identified research datasets
│   └── public/      Public research dataset
├── docs/            Research and developer documentation
├── figures/         Generated research figures
├── logs/            Analysis and verification audit logs
├── paper/           Automated LaTeX research paper
├── python/          Python analysis modules
├── R/               Independent R verification scripts
├── reports/         Generated tables and model summaries
├── schema/          Research data schema
└── tests/           Validation and test scripts
```

---

## Development workflow

A concise development workflow is documented in:

- `docs/DeveloperWorkflow.md`

Git and shell-history notes are documented in:

- `docs/GitTips.md`

> Ensure these files exist before committing the updated README so that the links remain valid.
