#!/usr/bin/env bash

tail -50 "$(ls -t logs/local/build_*.log | head -1)"