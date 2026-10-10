#!/bin/sh
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# Local dispatch. Uses the GitHub CLI. Does not embed a token.
set -eu
kind=${1:-journal}
title=${2:-Example}
gh workflow run desk.yml --ref main -f kind="$kind" -f title="$title"
gh run list --workflow desk.yml --limit 1
