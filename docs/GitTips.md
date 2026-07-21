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
