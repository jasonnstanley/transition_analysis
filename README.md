# Transition Analysis

Research software for analysing student transition pathways into first-year university mathematics.

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

The current case study analyses Autumn 2026 enrolments in 33130 Mathematical Modelling 1.

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

[![Python checks](https://github.com/jasonnstanley/transition_analysis/actions/workflows/python-checks.yml/badge.svg)](https://github.com/jasonnstanley/transition_analysis/actions/workflows/python-checks.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/jasonnstanley/transition_analysis)](https://github.com/jasonnstanley/transition_analysis/releases)
[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)