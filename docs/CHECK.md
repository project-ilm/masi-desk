# Check of the MASI desk, before its first release

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

Checked on 9 October 2026: the 42 files of `masi-desk.zip`, read against `desk-requirements.md`,
and run. As delivered, 15 of its 16 tests passed here; the sixteenth needed the OpenTimestamps
calendars and a signed-in `gh`, and failed without them. After the corrections below, 18 tests
pass with or without the network, and the gate `bash ops/verify.sh` passes 10 checks.

## Corrected before release

1. **The local server let any website change it.** It sent `Access-Control-Allow-Origin: *` and
   took `POST /api/token` and `POST /api/launch` from any origin, so a page open in the same
   browser could replace the loaded Zenodo token, or launch a venue as any recorded person.
   It now sends no CORS header and refuses a POST from another origin (`masi/server.py`).
2. **The blind salt went to `/tmp/masi-secrets` by default,** outside the folder and readable by
   other users. A salt is now refused unless `MASI_SECRET_STORE` names the unblinder's store
   (`masi/desk.py`).
3. **Blind arrival did not blind.** With blind on, the public venue repository still named the
   work's title and the author's DOI in `works/`, `matters/`, `events/` and `index/papers.json`.
   The index row hid the title field only. Blind submission is now refused, failing closed,
   until it is fixed: open item B1 below.
4. **The Candor statement was rewritten after it was stamped,** so its OpenTimestamps proof
   covered bytes that no longer existed. The statement now stays as stamped, with the proof
   beside it in `<digest>.proof.json` (`masi/provenance.py`).
5. **Keys of the wrong length were padded with zeros** into AES-GCM keys, which is a weak key.
   They are refused now (`masi/encryption.py`).
6. **`misty-guard-local` was a three-marker scan, not misty guard.** Disclosure checks belong to
   spiguard. It is named `local-marker-scan` now and says what it is.
7. **Stamp scratch files went to the system temporary directory;** they stay inside the venue.
8. **The GitHub adapter crashed when `gh` was not installed;** it reports `failed_external`.
9. **Venue commits were forced under "MASI desk <desk@masi.local>";** the operator's own git
   identity is kept, and the placeholder is used only where git has none.
10. **Neither workflow installed what the tests import,** so both would fail on GitHub; one ran
    one of the two test files; `desk.yml` spliced workflow inputs into a shell line, which is
    a script injection. Both are fixed.
11. **Tests that needed the network or a login** now accept an honest `failed_external`, and still
    refuse any invented stamp, DOI or login.
12. **The copyright line and the affiliation** on every source file, and the full GPL-3.0 text in
    `LICENSE`.

## Open against the canon, not fixed here

- **B1, blind arrival** (item 3). The public repository must carry only salted hashes;
  titles, author DOIs and work records belong with the unblinder.
- **The four existing pieces are re-implemented instead of used.** The canon says the desk
  uses them and does not replace them:
  - Tok records go to a local `registry/general/inbox` in each venue, not through tok-doi's
    registrar and `ingest.sh`.
  - Candor is a local in-toto v0.1 statement, not the governance Candor.
  - The guard is a marker scan, not misty guard or spiguard.
- **No transition carries a Candor attestation,** though the canon asks for one on every
  irreversible act.
- **Schemas:** only `schemas/event.json` exists; the canon lists some twenty records, each with
  a versioned schema.
- **Faces:** the role comes from a query string, not the signed-in account. The server takes
  the actor's name from the request body; a forge login is not verified.
- **Not found in the code:**
  - the co-author acceptance setting, and conflict declarations;
  - the review key's lifecycle: a per-review key, the editor's copy, rotation;
  - access events for a private review repository;
  - an appeal decided by someone other than the original decider;
  - a policy change as an event that applies forward only;
  - secret scanning before a public commit, and the refusal of a trade secret.
- **Gates:**
  - G1 treats "exempt" as an approval without the container's exemption switch.
  - G3 reads a `patent_unfiled` fact rather than the linked patent matter's state.
  - G5 does not warn on human-subjects work with no preregistration.

## Which canon

The copy of `desk-requirements.md` inside the archive, which is the one this release carries
and the code was written against, differs from the copy uploaded beside it in three places.
The uploaded copy's lines, verbatim:

- Invariants, line 30:
  > - Secrets are never committed, never written into an index, a log, or a pull-request comment.

  The archive's copy has four other invariants in its place: one event per transition,
  committed atomically; several state dimensions; when a commit is a disclosure; and the
  encryption envelope recorded in the policy. Its Security section still says secrets are
  never committed.
- Default switches, line 200:
  > `priority = on-accept`. `reviews = closed`. Blind off. Review-as-version off, so a review is `isReviewOf` unless the container says it is a version. Retraction-on-later-reject off. Co-author click-accept off. Conflict matching manual. IRB gate on for human subjects. Dataset mount through Misty to Zenodo when the file does not fit in git. Rebuttal rounds uncapped. Policy changes apply forward only.
- Set aside, line 206:
  > Floor plans, registration, visa letters, hotels. An ISBN minted from nothing. A patent, trademark, copyright, or IRB approval filed or granted by script. A publisher DOI invented by the desk. A trade secret in the forge. Optional paths on the default launch form. Building the desk on private repositories. A hard cap on review rounds. A hard-wired role.

The next release carries whichever copy is ruled canon.
