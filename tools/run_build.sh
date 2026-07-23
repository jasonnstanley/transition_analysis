#!/usr/bin/env bash

# mkdir -p logs/local

PYTHONUTF8=1 python -m python.build \
    | tee "logs/local/build_$(date +%Y%m%d_%H%M%S).log"