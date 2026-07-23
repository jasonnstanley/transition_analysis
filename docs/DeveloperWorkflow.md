
# Developer Workflow

This document describes the standard development workflow for the Transition Analysis Toolkit.

## Purpose

The workflow is designed to keep development reproducible, reviewable, and synchronised across computers.

Developers should:

- begin from the latest `main` branch
- work inside the project virtual environment
- run checks before committing
- review changes before staging
- create focused commits
- push completed work to GitHub

## Start a development session

Move to the repository root:

```bash
cd ~/Python/transition_analysis

git pull --rebase origin main

source .venv/bin/activate

python --version
git status

python -m python.build

python -m python.checks

python -m pytest

python -m python.analysis

python -m python.reports

git status --short

git diff

git diff path/to/file

git diff --stat

git add path/to/file

git add README.md

git add docs/DeveloperWorkflow.md

git diff --staged

git commit -m "Describe the completed change"

git commit -m "Add developer workflow documentation"

git status

git push origin main

git status

On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

##  Working across multiple computers

```text
When working on Windows, macOS, or another computer:

Push completed work before leaving the current computer.
Pull with rebase before starting work on another computer.
Avoid editing the same files independently on two computers.
Resolve any conflict before continuing development.
Confirm a clean working tree after each completed push.

Recommended starting command:
```

```bash
git pull --rebase origin main

git push origin main
git status

git pull --rebase origin main
source .venv/Scripts/activate		or		source .venv/bin/activate
python -m python.build
git status --short
git diff
git add path/to/file
git diff --staged
git commit -m "Describe the completed change"
git push origin main
git status



```