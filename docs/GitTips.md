# Git and Shell History Tips


This document is a practical reference for the Git commands used during development of the Transition Analysis Toolkit.

It is not intended to teach Git from first principles. Instead, it provides a concise collection of commands that are frequently used during normal development.

---

## Repository Status

### Current repository status:

```bash
git status

Compact status:										git status --short

Show current branch:								git branch
```

### Reviewing Changes
```bash
Review all unstaged changes:						git diff

Review a specific file:								git diff README.md

Review staged changes:								git diff --staged

Summarise changes:									git diff --stat
```


### Staging Files
```bash
Stage one file:										git add README.md

Stage multiple files:								git add file1 file2

Stage everything:									git add .

Interactive staging:								git add -p
```

### Commiting Changes
```bash
Create a commit:									git commit -m "Describe the completed change"

Amend the previous commit message:					git commit --amend
```

### Viewing History
```bash
Compact history:									git log --oneline

Graph view:											git log --oneline --graph --decorate

Recent history:										git log -10

Find previous commits:								git log --grep="README"
```

### Searching Command History
```bash
Search terminal history:							history | grep git

Search for previous README commands:				history | grep README

Reverse search:										Ctrl+r

Repeat previous command:							!!

Repeat previous command beginning with "git":		!git
```

### Inspecting Files
```bash
List tracked files:									git ls-files

Show ignored files:									git status --ignored

Show repository root:								git rev-parse --show-toplevel
```

### Synchronising
```bash
Download latest changes:							git fetch

Update local repository:							git pull --rebase origin main

Upload commits:										git push origin main
```

### Undoing Mistakes Safely
```bash
Unstage a file:										git restore --staged README.md

Discard unstaged changes:							git restore README.md

Restore every modified file:						git restore .
```

### Cleaning the Working Tree
```bash
Preview removable files:							git clean -n

Remove untracked files:								git clean -f

Remove untracked files and directories:				git clean -fd
```

### Tags
```bash
List tags:											git tag

Create a version tag:								git tag v0.5.0

Push tags:											git push --tags
```

## Typical Daily Workflow
```bash
git pull --rebase origin main
git status --short
git diff
git add README.md
git diff --staged
git commit -m "Describe the completed change"
git push origin main
git status
```

### Good Practice
```text
Make small, focused commits.
Review changes before staging.
Push completed work before changing computers.
Keep the main branch in a clean state.
Avoid committing generated files unless they are intended to be version controlled.
Prefer reproducible builds over manual edits to generated outputs.
```

I think this complements `DeveloperWorkflow.md` well. The workflow document explains **how to work**, while `GitTips.md` is the **terminal-side reference** you can quickly search or keep open in another window.

































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
