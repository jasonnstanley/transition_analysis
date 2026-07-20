# Transition Analysis Toolkit

A reproducible research toolkit for analysing student transition pathways into first-year university mathematics.


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

## Research context

The current case study analyses Autumn 2026 enrolments in a first stage undergraduate Mathematics subject.

The workflow was designed to support transparent and reproducible investigation of student transition pathways into first-year university mathematics.

## Repository structure

```text
transition_analysis/
├── python/          Python analysis modules
├── R/               Independent R verification scripts
├── schema/          Research data schema
├── data/
│   └── processed/   Approved de-identified research datasets
├── reports/         Generated tables and model summaries
├── figures/         Generated research figures
├── logs/            Analysis and verification audit logs
├── docs/            Project documentation
└── tests/           Validation and test scripts
```

[![Python checks](https://github.com/jasonnstanley/transition_analysis/actions/workflows/python-checks.yml/badge.svg)](https://github.com/jasonnstanley/transition_analysis/actions/workflows/python-checks.yml)

## Verified Platforms
```text
The Transition Analysis Toolkit has been successfully built and tested on:

- Windows 11
  - Python 3.14.5
  - R 4.6.1
  - TeX Live 2026

- macOS Monterey 12.7.6 (Intel)
  - Python 3.14.6
  - R 4.4.1
  - TeX Live 2022

The toolkit is designed to be reproducible across supported platforms.
```
## Developer Workflow
Start work - git pull --rebase origin main

Develop - python -m python.build

Commit - git add ..., git commit -m "..."

Synchronise - git pull --rebase origin main (good habit if using many platforms (local work or home, laptop or desktop etc) then, git push
```text
Summary:
git add .
git commit -m "Improve README formatting or some other informative comment"
git pull --rebase origin main
git push origin main
git status
```
## Search your command history for README
Summary:
```textSee commits that modified README.md

If instead you want the Git history of the file (rather than your terminal history), use:

git log -- README.md

or for a compact view:

git log --oneline -- README.md

To see exactly what changed in each commit:

git log -p -- README.md

These are worth remembering:

history | grep ... → What commands did I type?
git log -- README.md → When did the file change?

The distinction between shell history and Git history is one of the most useful habits to develop when working with Git.
```
history | grep README

or more specifically:

history | grep "git add"

or:

history | grep "README.md"

If you want to find the exact command where you staged the README, this is usually enough:

history | grep "git add README.md"
Interactive search (my favourite)

In Bash or Git Bash, press:

Ctrl + r

Then start typing:

README

or

git add

Each press of Ctrl + r searches further back through matching commands. Press Enter to reuse the command, or use the arrow keys to edit it before running.

See commits that modified README.md

If instead you want the Git history of the file (rather than your terminal history), use:

git log -- README.md

or for a compact view:

git log --oneline -- README.md

To see exactly what changed in each commit:

git log -p -- README.md

These are worth remembering:

history | grep ... → What commands did I type?
git log -- README.md → When did the file change?

The distinction between shell history and Git history is one of the most useful habits to develop when working with Git.


## GitHub
```text
Working files
      ↓
	git add
      ↓
Staging area
      ↓
git commit
      ↓
Local Git repository (your computer)
      ↓
	git push
      ↓
GitHub (remote repository) 
```

