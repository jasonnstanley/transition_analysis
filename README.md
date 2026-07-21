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
The repository accompanies a research case study while providing a reusable, transparent workflow for reproducible educational data analysis.


## Quick start

Clone the repository and enter the project directory:

```bash
git clone https://github.com/jasonnstanley/transition_analysis.git
cd transition_analysis
```

Create and activate a virtual environment.

### Windows Git Bash

```bash
py -m venv .venv
source .venv/Scripts/activate
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the Python dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Independent verification requires a working installation of **R**. When available, the canonical build automatically runs the independent R verification scripts.

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
