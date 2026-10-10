#!/usr/bin/env bash
# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
# masi-desk: the repository's own gate. Exit 0 when nothing fails; 1 on any failure.
# A check that needs what this machine lacks reports UNJUDGED, never PASS.
set -uo pipefail
cd "$(dirname "$0")/.."
mkdir -p .tmp
PASS=0; FAIL=0; UNJ=0
chk() { local id="$1" desc="$2" out rc; shift 2; out="$("$@" 2>&1)"; rc=$?
  if [ "$rc" -eq 0 ]; then printf '  PASS     %s  %s\n' "$id" "$desc"; PASS=$((PASS + 1))
  elif [ "$rc" -eq 3 ]; then printf '  UNJUDGED %s  %s: %s\n' "$id" "$desc" "$(printf '%s' "$out" | tail -1)"; UNJ=$((UNJ + 1))
  else printf '  FAIL     %s  %s\n' "$id" "$desc"; printf '%s\n' "$out" | tail -8 | sed 's/^/           /'; FAIL=$((FAIL + 1)); fi; }
files() { if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then git ls-files --cached --others --exclude-standard
          else find . -type f -not -path './.git/*' -not -path './.venv/*' -not -path './.tmp/*' | sed 's#^\./##'; fi; }
src() { files | grep -E '\.(py|sh|js|html|css|yml)$'; }
py() { [ -x .venv/bin/python ] && echo .venv/bin/python || echo python3; }

d01() { local bad; bad=$(src | while read -r f; do grep -q '© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.' "$f" || echo "$f"; done)
        [ -z "$bad" ] || { echo "no copyright line: $bad"; return 1; }; }
d02() { python3 -c "import json,sys; m=json.load(open('misty.json')); sys.exit(0 if all(c.get('affiliation')=='AyeAI' for c in m['creators']) else 1)" \
        && [ -z "$(grep -E '^ *affiliation:' CITATION.cff | grep -vE 'affiliation: *AyeAI$')" ]; }
d03() { if ! "$(py)" -c "import cryptography, misty" 2>/dev/null; then
          [ -n "${MASI_NO_VENV:-}" ] && { echo "cryptography or misty-doi is not importable"; return 3; }
          { python3 -m venv .venv && PIP_NO_CACHE_DIR=1 TMPDIR="$PWD/.tmp" .venv/bin/pip install -q -r requirements.txt; } >/dev/null 2>&1 \
            || { echo "could not install requirements.txt into ./.venv"; return 3; }
        fi
        mkdir -p logs
        # judged by unittest's exit code, never by where its summary lands among what the code under test prints
        PYTHONDONTWRITEBYTECODE=1 "$(py)" -m unittest tests/test_desk.py tests/test_platform.py > logs/unittest.log 2>&1
        local rc=$?
        grep -E '^(Ran [0-9]+ tests|OK|FAILED)' logs/unittest.log | tail -2
        [ "$rc" -eq 0 ] || { grep -E '^(FAIL|ERROR):' logs/unittest.log; echo "the full output is in logs/unittest.log"; return 1; }; }
d04() { local hit; hit=$(files | grep -v '^ops/verify.sh$' | xargs -d '\n' grep -lE 'ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{40,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|ZENODO_TOKEN=[A-Za-z0-9]{20,}' 2>/dev/null)
        [ -z "$hit" ] || { echo "a secret pattern in: $hit"; return 1; }; }
d05() { local hit; hit=$(grep -rn '"/tmp' masi bin 2>/dev/null); [ -z "$hit" ] || { echo "$hit"; return 1; }; }
d06() { ! grep -q 'Access-Control-Allow-Origin' masi/server.py && grep -q '_same_origin()' masi/server.py; }
d07() { local w; for w in .github/workflows/*.yml; do grep -q 'pip install -r requirements.txt' "$w" || { echo "$w installs nothing"; return 1; }
          if grep -E '^\s*(- )?run:.*\$\{\{ *github\.event\.inputs' "$w"; then echo "$w splices an input into a shell line"; return 1; fi; done; }
d08() { local hit; hit=$(files | grep -E '(^|/)__pycache__/|\.pyc$|\.tar\.gz$|^\.venv/'); [ -z "$hit" ] || { echo "$hit"; return 1; }; }
d09() { python3 - <<'PY'
import json, re, sys
m = json.load(open("misty.json"))["version"]
c = re.search(r"^version:\s*(\S+)", open("CITATION.cff").read(), re.M).group(1)
p = re.search(r'__version__ = "([^"]+)"', open("masi/__init__.py").read()).group(1)
sys.exit(0 if m == c == p else print(f"misty.json {m}, CITATION.cff {c}, masi/__init__.py {p}") or 1)
PY
}
d10() { local hit; hit=$(files | xargs -d '\n' grep -lE '10\.5281/zen''odo\.([^0-9]|$)|DOI-PEN''DING' 2>/dev/null); [ -z "$hit" ] || { echo "$hit"; return 1; }; }

echo "masi-desk: contract verification"
chk D01 "every source file carries the copyright line"                      d01
chk D02 "no affiliation other than AyeAI is claimed"                         d02
chk D03 "the test suite passes"                                              d03
chk D04 "no secret is committed"                                             d04
chk D05 "no default path under /tmp in the code"                             d05
chk D06 "the local server sends no wildcard CORS and refuses another origin" d06
chk D07 "the workflows install what they test and splice no input into a shell line" d07
chk D08 "no build artefacts"                                                 d08
chk D09 "misty.json, CITATION.cff and the package agree on the version"     d09
chk D10 "no placeholder DOI"                                                 d10
echo "  $PASS passed, $FAIL failed, $UNJ unjudged"
[ "$FAIL" -eq 0 ]
