# Contributing

Thank you for your interest in contributing to the Transition Analysis Toolkit.

This project aims to support transparent, reproducible research into student transition pathways and educational analytics. Contributions that improve reliability, reproducibility, documentation, testing, or usability are welcome.

## Before You Begin

Please:

- Read the project README.
- Review `docs/DeveloperWorkflow.md`.
- Check existing issues or discussions before starting major work.

## Development Workflow

1. Fork or clone the repository.
2. Create a focused branch for your work.
3. Make small, well-defined changes.
4. Run the canonical build:

```bash
python -m python.build
```

5. Ensure all tests pass:

```bash
python -m pytest
```

6. Review your changes:

```bash
git diff
```

7. Commit with a clear message.

8. Submit a pull request describing:

- what changed
- why it changed
- how it was verified

## Coding Standards

- Follow existing project style.
- Prefer readable code over clever code.
- Keep functions focused on a single responsibility.
- Document public modules and functions.
- Preserve reproducibility.

## Documentation

Documentation is considered part of the project.

If behaviour changes, update the relevant documentation in the same commit where practical.

## Testing

New functionality should include appropriate tests.

The repository should remain in a passing state after each contribution.

## Research Data

Do not commit identifiable student information.

Only approved de-identified research datasets belong in the public repository.

## Issues

Bug reports should include:

- operating system
- Python version
- steps to reproduce
- expected behaviour
- observed behaviour

## Pull Requests

Pull requests should remain focused on a single logical change.

Smaller pull requests are generally easier to review than large combined changes.

## Questions

If you are unsure about a proposed contribution, open an issue for discussion before undertaking major development.

Thank you for helping improve the Transition Analysis Toolkit.




### Development workflow

1. Create virtual environment

2. Install requirements

3. Run

    python -m python.checks

4. Run

    python -m python.build

5. Run

    python -m pytest

6. Submit Pull Request