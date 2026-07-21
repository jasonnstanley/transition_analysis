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
