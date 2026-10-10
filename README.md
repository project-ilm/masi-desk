# MASI desk

DOI: [10.5281/zenodo.23288683](https://doi.org/10.5281/zenodo.23288683)

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

SPDX-License-Identifier: GPL-3.0-or-later

Local rehearsal of the desk. It launches a journal, a conference, or a book, appends events, folds them into multi-dimensional state, and regenerates indexes.

Review text is sealed with AES-GCM. The public file holds ciphertext. G3 blocks a public mint, not an acceptance. G1 compares the approval date with the collection date. A book launch writes four chapter matters. A conference launch writes a track matter. Transitions are read from `transitions.json`. Roles are read from `permissions.json`.

This run does not mint a DOI, call Zenodo, stamp OpenTimestamps, or open a GitHub pull request. The outlet rehearsal still returns `pushed: false`.

```
python3 -m pip install -r requirements.txt
bash ops/verify.sh
python3 -m unittest tests/test_desk.py tests/test_platform.py
python3 -m masi launch journal "Example" --venue venue
```

Blind arrival is refused in this release, because the public repository still named the
work. `docs/CHECK.md` records what was checked, what was corrected before release, and what of
the canon is still open.
