cat > docs/DeveloperWorkflow.md <<'EOF'
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