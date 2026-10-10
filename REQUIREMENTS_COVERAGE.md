# Requirements coverage

© 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.

18 tests pass, with or without the network. A dry run is not a mint. No DOI was invented.
docs/CHECK.md lists what the canon asks for that this release does not yet do.

| Requirement | Implementation | Test | Status |
| --- | --- | --- | --- |
| Multiple independent venues | `Platform.launch` writes a directory per venue | `test_two_of_each_are_isolated` | COMPLETE |
| Person, login required to act | `records` person, `can_act` | `test_unlinked_person_cannot_act` | COMPLETE |
| Name change appends | `rename` | `test_name_change_appends` | COMPLETE |
| Git commit on launch | `gitprov.commit` returns `rev-parse` | isolation test | COMPLETE |
| Event parent conflict | `Store.append` | `test_parent_conflict` | COMPLETE |
| Journal matrix, no accept-to-publish | `transitions.json` | desk workflow tests | COMPLETE |
| G3 blocks mint not accept | `gates.py` | `test_g3_blocks_mint_not_acceptance` | COMPLETE |
| G1 date order | `gates.py` | `test_g1_date_and_book_chapters` | COMPLETE |
| AES-GCM review, keys of the right length only | `encryption.py` | `test_encryption_hides_plaintext`, `test_a_short_key_is_refused_not_padded` | COMPLETE |
| Blind arrival | `blind.py`; refused in `submit` | `test_blind_is_refused_until_it_stops_naming_the_work` | BLOCKED: the public repository named the work (CHECK B1) |
| A salt only in a named store | `submit` | `test_a_salt_needs_a_named_store_and_the_index_regenerates` | COMPLETE |
| Misty package and dry-run | `misty_bridge` | `test_matrix_is_bound_to_workflow_and_misty_is_called` | COMPLETE |
| Live Zenodo DOI | `pending_external` without `ZENODO_TOKEN`; no publish call with it either | `test_no_invented_doi_or_tok` | BLOCKED-BY-CREDENTIAL |
| Tok existence stamp | `ots stamp`; the proof kept as its AyeSHA placeholder; a local inbox, not the tok-doi registrar | `test_no_invented_doi_or_tok` | PARTIAL |
| Candor statement | in-toto statement, stamped, proof beside it; not wired to transitions | `test_no_invented_doi_or_tok` | PARTIAL |
| GitHub issue | `gh issue create` when `MASI_GITHUB_REPO` is set; a missing `gh` is reported | `test_no_invented_doi_or_tok` | EXTERNAL-CONFIGURED |
| Role faces | `/api/face` returns the role named in the query | server face route | PARTIAL |
