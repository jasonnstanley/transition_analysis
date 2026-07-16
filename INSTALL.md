# Installation Guide

## Requirements

- Python 3.14
- Git
- R (for independent verification)

## Clone the repository

```bash
git clone https://github.com/jasonnstanley/transition_analysis.git

cd transition_analysis
```

## Create a virtual environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Install dependencies

```bash
pip install -r requirements.txt
```

## Verify installation

```bash
python --version
pip list
```

The toolkit is now ready to use.